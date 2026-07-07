from dotenv import load_dotenv
load_dotenv()

from google import genai

client = genai.Client()  # automatically picks up GEMINI_API_KEY from environment
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Say hello and confirm you're working."
)
print(response.text)