import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(
    api_key=os.environ.get(API_KEY),
)

def response(subject, body):
    refine = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"{subject}-Subject\n {body}-Body\nThe above is the Subject and the Body of an Email summarize it and give a short Subject and Body for the Email.",
            }
        ],
        model="llama-3.3-70b-versatile",
    )

    print(refine.choices[0].message.content)
    return
