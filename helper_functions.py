from google import genai
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(API_KEY)

response = client.models.generate_content(
    model="gemini-1.5-flash", contents="Explain how AI works in a few words"
)
print(response.text)

# def response(subject, body):
#     #print("in helper_fn")
