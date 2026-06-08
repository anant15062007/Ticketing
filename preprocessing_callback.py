import re

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

def otp_check(text):
    #print("In otp check")
    otp_found = bool(re.search(r'\b\d{4,8}\b', text))
    #print(otp_found)
    if otp_found:
        text = re.sub(r'\b\d{4,8}\b', "[Contained OTP]", text)
    return text

def check_for_close_keyword(email_text):
    close_pattern = r"\b(?<!do not\s)(?<!don't\s)(close|closed|resolved|solved)\b"
    if re.search(close_pattern, email_text, re.IGNORECASE):
        return True
    return False