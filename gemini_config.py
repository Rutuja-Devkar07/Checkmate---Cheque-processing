import io
import os
import google.generativeai as genai
from dotenv import load_dotenv


load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("AIzaSyBAMnGqRHNgF-cOysTPXuO9X9mAPNMvpzk"))
model = genai.GenerativeModel("gemini-2.0-flash")
