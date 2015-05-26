# test_squad

#Install python package pip
    sudo apt-get install python-pip
#Install django 1.7
    sudo pip install django==1.7
#Install other python dependencies
    sudo pip install requests
    sudo pip install json
    sudo pip install gspread
    sudo pip install oauth2client


git clone https://github.com/vedansh/test_squad

# Modify test_squadrun/scrum/constants.py
    Look around slack api and make an account
    Register for an app
    Modify team_id , client_id , client_secret and channel_id in constants.py

    Download a json file for authentication purposes of google spreadsheet using this link below
    http://gspread.readthedocs.org/en/latest/oauth2.html
    copy this file to test_squadrun/scrum/ directory
    Modify spreadsheet_authentication   in constants file with the name of json file downloaded
    Create a spreadsheet and allow it to be shared with the email in json file
    Modify spreadsheet_name in constants file with the spreadsheet you created.


#Deploying and running the project
    #Go inside directory of test_squadrun
    cd test_squadrun
    # Run the project
    python manage.py runserver 127.0.0.1:80

    View the data in spreadsheet.

