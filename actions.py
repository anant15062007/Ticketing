import psycopg2
import os
import base64
import requests
import time
from email.message import EmailMessage
from googleapiclient.errors import HttpError
import re
from dotenv import load_dotenv

DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres:postgres@localhost:5432/ticketing_db"
)

load_dotenv()
API_KEY = os.getenv("GITHUB_TOKEN_KEY")

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
            message.set_content("Your ticket has been created at http://localhost:5173/.")

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

def is_github_comment_processed(comment_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT EXISTS(SELECT 1 FROM tickets_schema.processed_comments WHERE comment_id = %s);", (comment_id,))
    exists = cur.fetchone()[0]
    cur.close()
    conn.close()
    return exists

def get_routing_info_by_issue(issue_number):
    conn = get_db_connection()
    cur = conn.cursor()
    
    query = """
        SELECT thread_id, message_id, sender_email 
        FROM tickets_schema.issue_mappings 
        WHERE issue_number = %s 
        ORDER BY created_at DESC LIMIT 1;
    """
    cur.execute(query, (issue_number,))
    result = cur.fetchone()
    cur.close()
    conn.close()
    
    if result:
        return {
            "thread_id": result[0],
            "message_id": result[1],
            "sender_email": result[2]
        }
    return None

def log_processed_github_comment(comment_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO tickets_schema.processed_comments (comment_id) VALUES (%s) ON CONFLICT DO NOTHING;", (comment_id,))
    conn.commit()
    cur.close()
    conn.close()

def checkGithubForComment(service):

    url = f"https://api.github.com/repos/anant15062007/Tickets/issues/comments"
    
    headers = {
        "Authorization": f"token {API_KEY}",
        "Accept": "application/vnd.github.v3+json"
    }
    params = {
        "sort": "created",
        "direction": "desc",
        "per_page": 20
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            print(f"Failed to fetch comments from GitHub. Status Code: {response.status_code}")
            return

        comments = response.json()

        for comment in comments:
            comment_id = comment["id"]
            comment_body = comment["body"]
            
            if "----This is an automated comment----" in comment_body:
                continue
                
            if is_github_comment_processed(comment_id):
                continue
                
            issue_num = int(comment["issue_url"].split("/")[-1])
            
            routing_info = get_routing_info_by_issue(issue_num)
            
            if routing_info:
                target_thread_id = routing_info["thread_id"]
                last_msg_id = routing_info["message_id"]
                customer_email = routing_info["sender_email"]
                
                print(f"🎯 Found new developer comment ({comment_id}) on Issue #{issue_num}!")
                print(f"🔄 Routing message to customer: {customer_email}")
                
                # 5. Build fake/minimal mock headers to satisfy your existing sendMail structure
                # This saves you from having to hit the slow Gmail API GET endpoint!
                mock_headers = [
                    {"name": "From", "value": customer_email},
                    {"name": "Message-ID", "value": last_msg_id},
                    {"name": "Subject", "value": f"Ticket #{issue_num} Update"}
                ]
                
                try:
                    sendMail(service, target_thread_id, mock_headers, True)
                    
                    log_processed_github_comment(comment_id)
                    print(f"✅ Successfully emailed customer and logged Comment ID {comment_id}.\n")
                    
                except HttpError as gmail_err:
                    print(f"Gmail API transmission failed for Comment {comment_id}: {gmail_err}")
                except Exception as send_err:
                    print(f"Error handling email transmission execution: {send_err}")
            else:
                print(f"⚠️ Comment found on Issue #{issue_num}, but it doesn't match any thread in our DB.")
                
    except Exception as e:
        print(f"An error occurred while running the GitHub comment monitor: {e}")

def close_github_issue(issue_number):
    url = f"https://api.github.com/repos/anant15062007/Tickets/issues/{issue_number}"
    
    headers = {
        "Authorization": f"token {API_KEY}",
        "Accept": "application/vnd.github.v3+json"
    }

    payload = {
        "state": "closed",
        "state_reason": "completed"
    }
    
    try:
        response = requests.patch(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            print(f"🔒 Successfully CLOSED GitHub Issue #{issue_number}!")
            return True
        else:
            print(f"❌ Failed to close issue. Status Code: {response.status_code}")
            return False
    except Exception as e:
        print(f"Error connecting to GitHub while closing issue: {e}")
        return False
    
