import os.path
import os
import time
import base64
import json
import re
import google.auth
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from processing import guardRail
from actions import get_issue_from_db, find_threadID, find_messageID
from actions import sendMail, checkGithubForComment
from check_update import process_unsent_emails


# Use modify scope to allow marking as read without full account deletion powers
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']


def get_full_body(payload):
    """Recursively finds and decodes the plain text body from the payload."""
    body = ""
    parts = payload.get('parts')
    if parts:
        for part in parts:
            mimeType = part.get('mimeType')
            if mimeType == 'text/plain':
                data = part.get('body', {}).get('data', '')
                body += base64.urlsafe_b64decode(data).decode('utf-8')
            elif part.get('parts'):
                body += get_full_body(part)
    else:
        data = payload.get('body', {}).get('data', '')
        if data:
            body = base64.urlsafe_b64decode(data).decode('utf-8')
    return body

def get_unread_emails():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    if not creds:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('gmail', 'v1', credentials=creds)

        results = service.users().messages().list(userId='me', q='is:unread').execute()
        messages = results.get('messages', [])
        
        checkGithubForComment(service)
        
        process_unsent_emails()

        if not messages:
            print('No unread messages found.')
            return            

        print(f'Found {len(messages)} unread messages:')

        processed_threads = set()

        def markAsRead(identification):
                service.users().messages().modify(
                    userId='me', 
                    id=identification, 
                    body={'removeLabelIds': ['UNREAD']}
                ).execute()


        for message in messages:
            thread_id = message["threadId"]
            message_id = message['id']
            msg = service.users().messages().get(userId='me', id=message['id']).execute()
            headers = msg.get('payload', {}).get('headers', [])
            subject = next((header['value'] for header in headers if header['name'] == 'Subject'), 'No Subject')
            body = get_full_body(msg.get('payload', {}))

            sender_header = next((header['value'] for header in headers if header['name'] == 'From'), None)
            sender_email = "me"
            if sender_header:
                email_match = re.findall(r'<([^>]+)>', sender_header)
                sender_email = email_match[0] if email_match else sender_header


            if find_threadID(thread_id)==False:
                print("Therad ID:- ", thread_id)
                #print(message)
                if thread_id in processed_threads:
                    continue

                print(body)
                
                guardRail(subject, body, False, thread_id, message['id'], sender_email)

                processed_threads.add(thread_id)
                markAsRead(message['id'])
                sendMail(service, thread_id, headers, False)

            elif find_threadID(thread_id)==True and find_messageID(message_id)==False:
                print("It is a reply")
                guardRail(subject, body, True, thread_id, message['id'], sender_email)
                markAsRead(message['id'])
                sendMail(service, thread_id, headers, True)
                
            elif find_threadID(thread_id)==True and find_messageID(message_id)==True:
                markAsRead(message['id'])
                print("Already made a ticket and it is not a reply")

    except Exception as error:
        print(f'An error occurred: {error}')

def main_loop():
    print("Ticketing service started. Press Ctrl+C to stop.")
    while True:
        try:
            get_unread_emails()
        except Exception as e:
            print(f"Error during check: {e}")
        
        print("Waiting 60 seconds for next check...")
        time.sleep(60)

if __name__ == '__main__':
    main_loop()