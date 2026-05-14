import os
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GITHUB_TOKEN_KEY")

GITHUB_TOKEN = API_KEY
REPO_OWNER = "anant15062007"
REPO_NAME = "Tickets"

def create_github_issue(short_subject, short_body):
    url = f"https://api.github.com/repos/anant15062007/Tickets/issues"
    
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    data = {
        "title": short_subject,
        "body": short_body
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 201:
        print(f"Successfully created GitHub Issue: {response.json().get('html_url')}")
    else:
        print(f"Failed to create issue: {response.status_code}, {response.text}")

# --- Inside your loop after AI summarization ---
# ticket_data = json.loads(response.text)
# create_github_issue(ticket_data['short_subject'], ticket_data['short_body'])