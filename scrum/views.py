from django.shortcuts import render
from django.shortcuts import redirect
import constants

import requests
import json
import gspread
from oauth2client.client import SignedJwtAssertionCredentials

def index(request):
    if request.method == 'POST':
        if request.POST.get('login'):
            return redirect("https://slack.com/oauth/authorize?client_id=%s&scope=client&team=%s&redirect_uri=%s" %(constants.client_id,constants.team_id,constants.redirect_uri) )
    elif "access_token" in  request.session:
        return redirect('/scrum/channel/')
    else:
        return render(request, 'scrum/index.html')



def callback(request):
    if request.GET.get('code'):
        code = request.GET.get('code')
        url = "https://slack.com/api/oauth.access"
        params = {"client_id": constants.client_id, "client_secret": constants.client_secret ,"code": code}
        r = requests.get(url=url, params=params)
        #print r.text
        request.session["access_token"] =  json.loads(r.text)['access_token']
        request.session.modified = True
        # Getting user name
        url = "https://slack.com/api/auth.test"
        params = {"token":request.session["access_token"]}
        r = requests.get(url=url,params=params)
        request.session["username"] = json.loads(r.text)['user']
        request.session.modified = True
        return redirect('/scrum/channel/')
    else:
        return redirect('scrum/')

def validate_token(token):
    url = "https://slack.com/api/auth.test"
    params = {"token":token}
    r = requests.get(url=url, params=params)
    if 'ok' in json.loads(r.text):
        return json.loads(r.text)['ok']
    return False


def save_message_to_Sheet(user_name,message):
    json_key = json.load(open(constants.spreadsheet_authentication))
    scope = ['https://spreadsheets.google.com/feeds']

    credentials = SignedJwtAssertionCredentials(json_key['client_email'], json_key['private_key'], scope)
    gc = gspread.authorize(credentials)

    sh = gc.open(constants.spreadsheet_name)
    try:
	    worksheet = sh.worksheet(user_name)
    except gspread.WorksheetNotFound:
	    worksheet = sh.add_worksheet(title=user_name,rows="2", cols="1")
	    worksheet.update_cell(1, 1, user_name+"'s messages")

    worksheet.append_row([message])


def channel(request):
    if "access_token" not in  request.session:
        return redirect('/scrum/')
    if not validate_token(request.session["access_token"]):
        del request.session["access_token"]
        return redirect('/scrum/')
    if request.method == 'GET':
        return render(request ,'scrum/channel.html')

    elif request.method == 'POST':
        if request.POST.get('send_message'):
            message = request.POST.get('to_send')
        token = request.session["access_token"]
        username = request.session["username"]
        url = "https://slack.com/api/chat.postMessage"
        channel = constants.channel_id
        params = {"token": token, "channel": channel, "text":message, "as_user": username}
        r = requests.get(url=url,params=params)
        save_message_to_Sheet(username,message)
        return redirect('/scrum/channel/')

def getuser_list(token):
    url = "https://slack.com/api/users.list"
    #token = request.session["access_token"]
    params = {"token": token}
    r=requests.get(url=url,params=params)
    user_list={}
    members=[]
    if "members" in json.loads(r.text):
        members=json.loads(r.text)['members']
    for member in members:
        user_list[member["id"]]=member["name"]
    return user_list

def getmessage_list(messages,user_dict):
    user_msg=[]
    for message in messages:
        if "user" in message and "text" in message and message["user"] in user_dict:
            user_msg.append({"username":user_dict[message["user"]],"message":message["text"]})
    return user_msg


def display(request):
    if "access_token" not in  request.session:
        return redirect('/scrum/')
    if not validate_token(request.session["access_token"]):
        del request.session["access_token"]
        return redirect('/scrum/')
    user_msg=[]
    token = request.session["access_token"]
    user_dict=getuser_list(token)
    url = "https://slack.com/api/channels.history"
    channel = constants.channel_id
    params = {"token": token,"channel": channel}
    r=requests.get(url=url,params=params)
    user_msg=getmessage_list(json.loads(r.text)['messages'],user_dict)
    return render(request, 'scrum/display.html', {"user_msg":user_msg})


def logout(request):
    if "access_token" in  request.session:
        del request.session ["access_token"]
    return redirect('/scrum/')


