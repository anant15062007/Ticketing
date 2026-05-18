import re
import json
from helper_functions import response
import sys
import preprocessing_callback

is_reply = False
current_module = sys.modules["preprocessing_callback"]


def guardRail(subject, body, is_reply, thread_id, config_path='guardrail.json'):

    with open(config_path, 'r') as f:
        config = json.load(f)

    processed_subject = subject
    processed_body = body

    for guardrail in config['guardrails']:
        action_name = guardrail['callback_action']
        callback = getattr(current_module, action_name)
        processed_subject = callback(processed_subject)
        processed_body = callback(processed_body)
        #print(processed_body)
    #print(processed_text)

    ### Check if the mail is a reply

    response(processed_subject, processed_body, is_reply, thread_id)



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