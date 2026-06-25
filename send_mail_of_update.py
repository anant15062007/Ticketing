import os
import base64 # <--- NEW IMPORT REQUIRED
import requests
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import HttpError, build
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from email.message import EmailMessage

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

creds = None
if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)

if not creds or not creds.valid: # Added 'not creds.valid' as a safety check
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
    with open('token.json', 'w') as token:
        token.write(creds.to_json())

service = build('gmail', 'v1', credentials=creds)

def sendUpdateMail(mailId, ticketId):
    try:
        message = EmailMessage()
        
        message.set_content(f"Your Ticket #{ticketId} has been updated at http://localhost:5173/.")

        message["To"] = mailId
        message["From"] = "jainanant469@gmail.com"
        message["Subject"] = "Ticket Update"

        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        
        create_message = {
            'raw': encoded_message
        }
        
        send_message = (
            service.users()
            .messages()
            .send(userId="me", body=create_message)
            .execute()
        )
        print(f'Website Update Reply Sent to {mailId}!')
        
    except HttpError as error:
        print(f"An error occurred: {error}")
        send_message = None
        
    return send_message

def send_agent_invite(mailId, password):
    try:
        message = EmailMessage()
        
        message.set_content(f"Your Agent ID is {mailId} and your password is {password}")

        message["To"] = mailId
        message["From"] = "jainanant469@gmail.com"
        message["Subject"] = "Credentials"

        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        
        create_message = {
            'raw': encoded_message
        }
        
        send_message = (
            service.users()
            .messages()
            .send(userId="me", body=create_message)
            .execute()
        )
        print(f'{mailId} Agent Added')
        
    except HttpError as error:
        print(f"An error occurred: {error}")
        send_message = None
        
    return send_message