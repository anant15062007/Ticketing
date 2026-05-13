import re
import json
#from helper_functions import response

def guardRail(subject, body, config_path='guardrail.json'):
    with open(config_path, 'r') as f:
        config = json.load(f)

    patterns = config['sensitive_patterns']
    any_sensitive_info = False

    for label, pattern in patterns.items():
        if re.search(pattern, subject) or re.search(pattern, body):
            print(f"Found sensitive info: {label}")
            any_sensitive_info = True
            break

    if not any_sensitive_info:
        print(f"\n--- NEW TICKET ---")
        print(f"Subject: {subject}")
        print(f"Body: {body}")