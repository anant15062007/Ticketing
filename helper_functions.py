import os
import json
from dotenv import load_dotenv
from groq import Groq
from issueCreation import create_github_issue
#import instructor
#from pydantic import BaseModel, Field, field_validator

load_dotenv()
API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(
    api_key=os.environ.get(API_KEY),
)

def response(subject, body, is_reply, thread_id):
    prompt = f"""Act as an efficient office assistant. Your task is to summarize incoming emails into a concise ticketing format.

### INSTRUCTIONS:
1. CORE CONTENT: Extract only the essential message. Ignore signatures, university rankings, standard disclaimers, and "Sent from my iPhone" style noise.
2. SUBJECT: Shorten the subject to a few words that capture the main topic.
3. BODY: Summarize the primary action or information into one clear sentence.
4. "AS-IS" RULE: If the Subject or Body is already short (less than 10 words) and clear, do not edit them. Return them exactly as they are.
5. SENSITIVE DATA: Do not invent names or details. Only use what is provided in the text.
6. If you see [Contained Email address] or [Contained Phone Number] leave it as it is.

### INPUT DATA:
Subject:{subject}
Body:{body}

### OUTPUT:
Return ONLY a valid JSON object. Do not include any introductory or concluding text. 
Use the following format:
{{
  "short_subject": "Extracted Subject here",
  "short_body": "Extracted Body here"
}}
"""
    
    refine = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="llama-3.3-70b-versatile",
    )

    raw_response = refine.choices[0].message.content
    #print(raw_response)
    ticket_json = json.loads(raw_response)
    final_subject = ticket_json["short_subject"]
    final_body = ticket_json["short_body"]
    print(final_body)
    create_github_issue(final_subject, final_body, is_reply, thread_id)
    return



# ### OUTPUT FORMAT (JSON):
# {
#   "short_subject": "...",
#   "short_body": "..."
# }