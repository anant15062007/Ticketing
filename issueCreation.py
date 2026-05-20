import os
import requests
import json
from dotenv import load_dotenv
from updating import update_issue
import psycopg2
from actions import get_issue_from_db
from comment import addComment

load_dotenv()
API_KEY = os.getenv("GITHUB_TOKEN_KEY")

DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres:postgres@localhost:5432/ticketing_db"
)


def get_db_connection():
    return psycopg2.connect(DATABASE_URL)


def save_issue_to_db(thread_id, issue_number, message_id, sender_email):
    conn = get_db_connection()
    cur = conn.cursor()

    query = """
        INSERT INTO tickets_schema.issue_mappings (message_id, thread_id, issue_number, sender_email)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (message_id)
        DO NOTHING;
    """
    
    cur.execute(query, (message_id, thread_id, issue_number, sender_email))
    conn.commit()
    cur.close()
    conn.close()

def changeMessageID(thread_id, message_id):
    conn = get_db_connection()
    cur = conn.cursor()
    query = """
        UPDATE tickets_schema.issue_mappings
        SET message_id = %s
        WHERE thread_id = %s;
    """
    try:
        cur.execute(query, (message_id, thread_id))
        conn.commit()
        print(f"🔄 Database Updated: Thread {thread_id} is now pointing to Message ID: {message_id}")
        return True
    except Exception as e:
        print(f"❌ Failed to update message_id in database: {e}")
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()

def create_github_issue(short_subject, short_body, is_reply, thread_id, message_id, sender_email):
    url = f"https://api.github.com/repos/anant15062007/Tickets/issues"
    
    headers = {
        "Authorization": f"token {API_KEY}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    data = {
        "title": short_subject,
        "body": short_body
    }

    
    if is_reply:
        #print("Have to update issue")
        issue_number = get_issue_from_db(thread_id)
        print(short_body)
        addComment(issue_number, short_subject, short_body)
        changeMessageID(thread_id, message_id)
    else:
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 201:
            print(f"Successfully created GitHub Issue: {response.json().get('html_url')}")
            #sendMail(response.json().get('html_url'))
            issue_number = response.json().get('number')
            save_issue_to_db(thread_id, issue_number, message_id, sender_email)
        else:
            print(f"Failed to create issue: {response.status_code}, {response.text}")