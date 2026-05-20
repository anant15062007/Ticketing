import re
import json
from helper_functions import response
import sys
from preprocessing_callback import check_for_close_keyword
from issueCreation import create_github_issue
from actions import close_github_issue, get_issue_from_db

current_module = sys.modules["preprocessing_callback"]


def guardRail(subject, body, is_reply, thread_id, message_id, sender_email, config_path='guardrail.json'):

    with open(config_path, 'r') as f:
        config = json.load(f)

    processed_subject = subject
    processed_body = body

    for guardrail in config['guardrails']:
        action_name = guardrail['callback_action']
        callback = getattr(current_module, action_name)
        processed_subject = callback(processed_subject)
        processed_body = callback(processed_body)
    
    isClose = check_for_close_keyword(body)

    if isClose==False:
        create_github_issue(processed_subject, processed_body, is_reply, thread_id, message_id, sender_email)
        response(processed_subject, processed_body, is_reply, thread_id)
    elif isClose==True:
        issue_number = get_issue_from_db(thread_id)
        close_github_issue(issue_number)
        print(f"Closed Issue {issue_number}")