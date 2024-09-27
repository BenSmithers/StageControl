from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

import os 

import numpy as np 
import base64
from email.message import EmailMessage

from time import time 

import json

main_email_file = os.path.join(
    os.path.dirname(__file__),
    "data",
    "default_email.json"
)

_obj = open(main_email_file,'rt')
sender_email = json.load(_obj)["email"]
_obj.close()

shift_file = os.path.join(
    os.path.dirname(__file__),
    "data",
    "shifter_data.csv"
)
def send_alert(warning_message, warning_headline="Something Wrong!"):
    """
        Lookup the current shifter from the CSV file, and email them with the provided warning data
    """
    now = time()
    email_data = np.loadtxt(shift_file, delimiter=",", dtype="str").T
    
    times = email_data[0].astype(float)
    shifter1 = email_data[1]
    shifter2 = email_data[2]

    index = np.searchsorted(times, now)-1
    if index<0:
        index=0
    
    _send_alert([shifter1[index],], warning_message, warning_headline)


def _send_alert(shifter_emails:'list[str]', warning_message, warning_headline="Something Wrong!"):
    """
        Sends an email to the given email with provided messages

        Also sends an email to the the main wctealerts address
    """
    
    recipients = shifter_emails
    recipients.append(sender_email)
    for recipient in recipients:
        SCOPES = ['https://mail.google.com/']

        creds_file = os.path.join(os.path.dirname(__file__), "data","DONOTCOMMIT.json")

        creds = None
        # try to find an existing token
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                print("refreshing")
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    creds_file, SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        service = build('gmail', 'v1', credentials=creds)
        results = service.users().labels().list(userId='me').execute()

        msg = EmailMessage()


        msg["To"]       = recipient
        msg["From"]     = "The WCTE Alert Bot"
        msg["Subject"]  = "WCTE Alert! {}".format(warning_headline)

        message = """
            Dear Shifter, 

            You are receiving this message because you are currently on shift. {} 

            Please Do Something, 
            The WCTE Water Alert Notification System 
        """.format(warning_message)

        msg.set_content(message)
        encoded_message = base64.urlsafe_b64encode(msg.as_bytes()).decode()

        create_message = {
                    'raw': encoded_message
        }

        send_message = (service.users().messages().send
                        (userId="me", body=create_message).execute())