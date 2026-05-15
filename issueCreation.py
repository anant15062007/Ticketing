import os
import requests
import json
from dotenv import load_dotenv
from updating import update_issue

load_dotenv()
API_KEY = os.getenv("GITHUB_TOKEN_KEY")

def create_github_issue(short_subject, short_body, is_reply, thread_id):
    url = f"https://api.github.com/repos/anant15062007/Tickets/issues"
    
    headers = {
        "Authorization": f"token {API_KEY}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    data = {
        "title": short_subject,
        "body": short_body
    }

    ### Database functions
    DB_FILE = "database.json"

    def save_issue_to_db(thread_id, issue_number):
        data = {}

        if os.path.exists(DB_FILE):
            with open(DB_FILE, 'r') as file:
                try:
                    data = json.load(file)
                except json.JSONDecodeError:
                    data = {}

        data[thread_id] = issue_number

        with open(DB_FILE, 'w') as file:
            json.dump(data, file, indent=4)

    def get_issue_from_db(thread_id):
        if not os.path.exists(DB_FILE):
            return None
        with open(DB_FILE, 'r') as file:
            try:
                data = json.load(file)
                return data.get(thread_id)
            except json.JSONDecodeError:
                return None
    
    if is_reply:
        #print("Have to update issue")
        issue_number = get_issue_from_db(thread_id)
        print(short_body)
        update_issue(issue_number, short_body)
    else:
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 201:
            print(f"Successfully created GitHub Issue: {response.json().get('html_url')}")
            issue_number = response.json().get('number')
            save_issue_to_db(thread_id, issue_number)
        else:
            print(f"Failed to create issue: {response.status_code}, {response.text}")