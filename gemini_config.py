import io
import os
import google.generativeai as genai
from dotenv import load_dotenv


load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv(your_api_key))
model = genai.GenerativeModel("gemini-2.0-flash")

