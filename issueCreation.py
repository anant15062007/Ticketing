import os
import requests
import json
from dotenv import load_dotenv
from updating import update_issue
import psycopg2
from actions import get_issue_from_db

load_dotenv()
API_KEY = os.getenv("GITHUB_TOKEN_KEY")

DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres:postgres@localhost:5432/ticketing_db"
)


def get_db_connection():
    return psycopg2.connect(DATABASE_URL)


def save_issue_to_db(thread_id, issue_number, message_id):
    conn = get_db_connection()
    cur = conn.cursor()

    query = """
        INSERT INTO tickets_schema.issue_mappings (message_id, thread_id, issue_number)
        VALUES (%s, %s, %s)
        ON CONFLICT (message_id) 
        DO NOTHING;
    """
    
    cur.execute(query, (message_id, thread_id, issue_number))
    conn.commit()
    cur.close()
    conn.close()


def create_github_issue(short_subject, short_body, is_reply, thread_id, message_id):
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
        update_issue(issue_number, short_body)
    else:
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 201:
            print(f"Successfully created GitHub Issue: {response.json().get('html_url')}")
            #sendMail(response.json().get('html_url'))
            issue_number = response.json().get('number')
            save_issue_to_db(thread_id, issue_number, message_id)
        else:
            print(f"Failed to create issue: {response.status_code}, {response.text}")