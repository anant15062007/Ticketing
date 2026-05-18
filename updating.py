import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GITHUB_TOKEN_KEY")

def update_issue(issue_number, body):
    url = f"https://api.github.com/repos/anant15062007/Tickets/issues/{issue_number}"
    
    headers = {
        "Authorization": f"token {API_KEY}",
        "Accept": "application/vnd.github.v3+json"
    }

    get_response = requests.get(url, headers=headers)
    if get_response.status_code != 200:
        print("Failed to fetch original issue")
        return
    old_body = get_response.json().get("body", " ")
    combined_body = f"{old_body}\n\n---\n**Update:**\n{body}"

    data = {"body": combined_body}
    response = requests.patch(url, headers=headers, json=data)
    
    if response.status_code == 200:
        #print(body)
        print(f"Successfully updated Issue #{issue_number}")
    else:
        print(f"Failed to update: {response.status_code}, {response.text}")