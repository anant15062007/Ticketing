import re
import json
from helper_functions import response
import sys
import preprocessing_callback

current_module = sys.modules["preprocessing_callback"]


def guardRail(subject, body, is_reply, thread_id, message_id, config_path='guardrail.json'):

    with open(config_path, 'r') as f:
        config = json.load(f)

    processed_subject = subject
    processed_body = body

    for guardrail in config['guardrails']:
        action_name = guardrail['callback_action']
        callback = getattr(current_module, action_name)
        processed_subject = callback(processed_subject)
        processed_body = callback(processed_body)
    print(processed_body)
    #print(processed_text)

    ### Check if the mail is a reply

    response(processed_subject, processed_body, is_reply, thread_id, message_id)