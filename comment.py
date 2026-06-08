import requests
import os
from dotenv import load_dotenv
from actions import cleanup

load_dotenv()
API_KEY = os.getenv("GITHUB_TOKEN_KEY")

def addComment(issue_number, subject, body):

    body = cleanup(body)

    url = f"https://api.github.com/repos/anant15062007/Tickets/issues/{issue_number}/comments"
    
    headers = {
        "Authorization": f"token {API_KEY}",
        "Accept": "application/vnd.github.v3+json"
    }

    bot_signature = "\n----This is an automated comment----\n"
    
    payload = {
        "body": f"{body}{bot_signature}"
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 201 or response.status_code == 200:
            print(f"Successfully posted new comment to Issue #{issue_number}!")
            return True
        else:
            print(f"Failed to add comment. Status Code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"An error occurred connecting to GitHub: {e}")
        return False