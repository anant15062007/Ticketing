import psycopg2
import os
import base64
from email.message import EmailMessage
from googleapiclient.errors import HttpError
import re

DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres:postgres@localhost:5432/ticketing_db"
)

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

def get_issue_from_db(thread_id):

    conn = get_db_connection()
    cur = conn.cursor()
    
    query = "SELECT issue_number FROM tickets_schema.issue_mappings WHERE thread_id = %s;"
    cur.execute(query, (thread_id,))
    
    result = cur.fetchone()
    
    cur.close()
    conn.close()
    
    return result[0] if result else None

def find_threadID(thread_id):

    conn = get_db_connection()
    cur = conn.cursor()
    
    query = "SELECT EXISTS(SELECT 1 FROM tickets_schema.issue_mappings WHERE thread_id = %s);"
    
    cur.execute(query, (thread_id,))
    exists = cur.fetchone()[0]
    
    cur.close()
    conn.close()
    
    return exists

def find_messageID(message_id):

    conn = get_db_connection()
    cur = conn.cursor()
    
    query = "SELECT EXISTS(SELECT 1 FROM tickets_schema.issue_mappings WHERE message_id = %s);"
    
    cur.execute(query, (message_id,))
    exists = cur.fetchone()[0]
    
    cur.close()
    conn.close()
    
    return exists

def sendMail(service, thread_id, headers, isComment):
    try:
        message = EmailMessage()
        issueNo = get_issue_from_db(thread_id)

        sender_header = next((header['value'] for header in headers if header['name'] == 'From'), None)
        sender_email = "me"
        if sender_header:
            email_match = re.findall(r'<([^>]+)>', sender_header)
            sender_email = email_match[0] if email_match else sender_header

        incoming_msg_id = next((header['value'] for header in headers if header['name'].lower() == 'message-id'), None)
        incoming_subject = next((header['value'] for header in headers if header['name'] == 'Subject'), 'No Subject')

        if not incoming_subject.lower().startswith("re:"):
            reply_subject = f"Re: {incoming_subject}"
        else:
            reply_subject = incoming_subject

        if issueNo is not None:
            if isComment==False:
                message.set_content(f"""This is an automated confirmation mail.
Your ticket has been created at https://github.com/anant15062007/Tickets/issues/{issueNo}""")
            else:
                message.set_content(f"""This is an automated confirmation mail.
Your ticket has been updated at https://github.com/anant15062007/Tickets/issues/{issueNo}""")
        else:
            message.set_content("An Error Occurred during ticket processing.")

        message["To"] = sender_email
        message["From"] = "jainanant469@gmail.com"
        message["Subject"] = reply_subject

        if incoming_msg_id:
            message["In-Reply-To"] = incoming_msg_id
            message["References"] = incoming_msg_id

        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        create_message = {
            "raw": encoded_message,
            "threadId": thread_id
        }
        
        send_message = (
            service.users()
            .messages()
            .send(userId="me", body=create_message)
            .execute()
        )
        print(f'Threaded Reply Sent! Message Id: {send_message["id"]}')
        
    except HttpError as error:
        print(f"An error occurred: {error}")
        send_message = None
        
    return send_message

def cleanup(body):
    if not body:
        return ""

    gmail_quote_pattern = r"On\s+[A-Za-z]{3},\s+[A-Za-z]{3}\s+\d+.*wrote:"
    
    parts = re.split(gmail_quote_pattern, body, flags=re.IGNORECASE)
    clean_body = parts[0]
    alternative_markers = [
        "___________", 
        "--- Original Message ---", 
        "From:", 
        "________________________________"
    ]
    
    for marker in alternative_markers:
        if marker in clean_body:
            clean_body = clean_body.split(marker)[0]

    return clean_body.strip()