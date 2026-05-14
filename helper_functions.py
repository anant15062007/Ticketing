import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(
    api_key=os.environ.get(API_KEY),
)

def response(mail):
    prompt = f"""Act as an efficient office assistant. Your task is to summarize incoming emails into a concise ticketing format.

### INSTRUCTIONS:
1. CORE CONTENT: Extract only the essential message. Ignore signatures, university rankings, standard disclaimers, and "Sent from my iPhone" style noise.
2. SUBJECT: Shorten the subject to a few words that capture the main topic.
3. BODY: Summarize the primary action or information into one clear sentence.
4. "AS-IS" RULE: If the Subject or Body is already short (less than 10 words) and clear, do not edit them. Return them exactly as they are.
5. SENSITIVE DATA: Do not invent names or details. Only use what is provided in the text.

### INPUT DATA:
Subject+Body:{mail}

### OUTPUT:
Give the output as a string
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

    print(refine.choices[0].message.content)
    return



# ### OUTPUT FORMAT (JSON):
# {
#   "short_subject": "...",
#   "short_body": "..."
# }