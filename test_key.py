import os
import google.generativeai as genai
from dotenv import load_dotenv

# Force load the .env file
load_dotenv()

key = os.getenv("GOOGLE_API_KEY")

print(f"1. Key found in .env? {'YES' if key else 'NO'}")
if key:
    print(f"2. Key starts with: {key[:5]}...")

try:
    genai.configure(api_key=key)
    model = genai.GenerativeModel('gemini-2.0-flash')
    response = model.generate_content("Say hello")
    print(f"3. Google Response: {response.text}")
    print("✅ SUCCESS: API Key is working!")
except Exception as e:
    print(f"❌ ERROR: {e}")