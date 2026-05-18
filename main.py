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
from email.message import EmailMessage
from actions import get_issue_from_db


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
            if get_issue_from_db(thread_id)==None:
                #print("Therad ID:- ", thread_id)
                #print(message)

                if thread_id in processed_threads:
                    continue

                msg = service.users().messages().get(userId='me', id=message['id']).execute()
                headers = msg.get('payload', {}).get('headers', [])
                subject = next((header['value'] for header in headers if header['name'] == 'Subject'), 'No Subject')
                body = get_full_body(msg.get('payload', {}))
                #print(body)

                is_reply = any(h['name'].lower() == 'in-reply-to' for h in headers)
                
                guardRail(subject, body, is_reply, thread_id)

                processed_threads.add(thread_id)

                markAsRead(message['id'])

                                

                
                def sendMail():
                    #print("Sending Mail")
                    try:
                        message = EmailMessage()
                        issueNo = get_issue_from_db(thread_id)
                        sender_header = next((header['value'] for header in headers if header['name'] == 'From'), None)

                        if sender_header:
                            email = re.findall(r'<([^>]+)>', sender_header)
                            sender_email = email[0] if email else sender_header

                        message.set_content(f"""This is automated draft mail
Your ticket has been created at https://github.com/anant15062007/Tickets/issues/{issueNo}""")

                        message["To"] = sender_email
                        message["From"] = "jainanant469@gmail.com"
                        message["Subject"] = "Ticket created"

                        # encoded message
                        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

                        create_message = {"raw": encoded_message}
                        # pylint: disable=E1101
                        send_message = (
                            service.users()
                            .messages()
                            .send(userId="me", body=create_message)
                            .execute()
                        )
                        print(f'Message Id: {send_message["id"]}')
                    except HttpError as error:
                        print(f"An error occurred: {error}")
                        send_message = None
                    return send_message


                sendMail()



            else:
                markAsRead(message['id'])
                print("Already in database")


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