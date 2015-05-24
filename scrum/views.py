from django.shortcuts import render
from django.shortcuts import redirect, HttpResponse
import requests
import json
import time
from slackclient import SlackClient

def index(request):
    if request.method == 'POST':
        if request.POST.get('login'):
            return redirect("https://slack.com/oauth/authorize?client_id=5036120771.5043912009&scope=client&team=T05123JNP")
    elif "access_token" in  request.session:
        return redirect('/scrum/channel/')
    else:
        return render(request, 'scrum/index.html')



def callback(request):
    if request.GET.get('code'):
        code = request.GET.get('code')
        url = "https://slack.com/api/oauth.access"
        params = {"client_id": "5036120771.5043912009", "client_secret": "da18ac610f63cf9ab855edd568cb2aa4" ,"code": code}
        r = requests.get(url=url, params=params)
        # Getting access token
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
        channel = "C05123K29"
        params = {"token": token, "channel": channel, "text":message, "as_user": username}
        r = requests.get(url=url,params=params)
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
    #if request.method == 'POST':
    #if request.POST.get('display'):
    token = request.session["access_token"]
    user_dict=getuser_list(token)
    url = "https://slack.com/api/channels.history"
    channel = "C05123K29"
    params = {"token": token,"channel": channel}
    r=requests.get(url=url,params=params)
    user_msg=getmessage_list(json.loads(r.text)['messages'],user_dict)
    return render(request, 'scrum/display.html', {"user_msg":user_msg})


def logout(request):
    if "access_token" in  request.session:
        del request.session ["access_token"]
        return redirect('/scrum/')


