import re
import json
from helper_functions import response

def guardRail(subject, body, config_path='guardrail.json'):

    email_found = False
    phone_found = False

    def email_check(text):
        #print("In email check")
        email_found = bool(re.search(r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b', text))
        if email_found:
            text = re.sub(r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b', "[Contained Email address]", text)
        return text

    def phone_check(text):
        #print("In phone check")
        phone_found = bool(re.search(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text))
        if phone_found:
            text = re.sub(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', "[Contained Phone Number]", text)
        return text

    CALLBACK_MAP = {
    "email_check": email_check,
    "phone_check": phone_check
    }

    with open(config_path, 'r') as f:
        config = json.load(f)

    processed_text = subject + " " + body

    for guardrail in config['guardrails']:
        action_name = guardrail['callback_action']
        
        if action_name in CALLBACK_MAP:
            callback_func = CALLBACK_MAP[action_name]
            processed_text = callback_func(processed_text)
    #print(processed_text)
    response(processed_text)



    # patterns = config['guardrails']
    # for label, pattern in patterns.items():
    #     if email_found:
    #         print(f"Found sensitive info: {label}")
    #         any_sensitive_info = True
    #         break

    # if not any_sensitive_info:
    #     # print(f"\n--- NEW TICKET ---")
    #     # print(f"Subject: {subject}")
    #     # print(f"Body: {body}")
    #     response(subject, body)




# for guardrail in config['guardrails']:
#     action_name = guardrail['callback_action']
    
#     # Retrieve the function from our map and call it
#     if action_name in CALLBACK_MAP:
#         callback_func = CALLBACK_MAP[action_name]
#         # Example: call the function on some text
#         result = callback_func("Sample Email Body")
#     else:
#         #Send to API as is



# # 1. Define your actual functions (callbacks)
# def redact_sensitive_info(text):
#     print("Executing Redaction...")
#     return "[CLEANED TEXT]"

# def flag_for_review(text):
#     print("Flagging for manual review...")
#     return text

# # 2. Map the JSON strings to the Python functions
# CALLBACK_MAP = {
#     "redact_sensitive_info": redact_sensitive_info,
#     "flag_for_review": flag_for_review
# }

# # 3. Load and execute
# with open('guardrails_definitions.json', 'r') as f:
#     config = json.load(f)