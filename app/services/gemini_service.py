import os
import google.generativeai as genai
from dotenv import load_dotenv
from app.services.rag_service import get_relevant_context

load_dotenv()

GEN_AI_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GEN_AI_KEY)

# Using the powerful Flash 2.0 model
model = genai.GenerativeModel(model_name="gemini-2.0-flash")

def get_chat_response(user_message):
    try:
        # 1. Retrieve potential matches from your JECRC PDF
        context = get_relevant_context(user_message)
        
        # 2. Construct the "Dual-Brain" Prompt
        prompt = f"""
        You are the official AI Assistant for JECRC University. You have two sources of knowledge:
        1. The **Context** provided below (Official University Data).
        2. Your **General Knowledge** (Google Gemini).

        OFFICIAL UNIVERSITY CONTEXT:
        ---------------------
        {context}
        ---------------------

        USER QUESTION: "{user_message}"

        INSTRUCTIONS:
        - **Rule 1 (College Queries):** If the user asks about JECRC (Admissions, Fees, Campus, Placements), you MUST derive the answer from the "OFFICIAL UNIVERSITY CONTEXT" above. 
          - If the specific detail is missing in the context, politely provide the admissions email (admission@jecrcu.edu.in) instead of making up a number.
        
        - **Rule 2 (General Queries):** If the user asks a general question (e.g., "What is Python?", "Who is Elon Musk?", "Write a poem"), IGNORE the University Context and answer using your General Knowledge. Be helpful and smart.

        - **Rule 3 (Identity):** Always maintain a professional, academic tone. Even when answering general questions, act like a helpful university assistant.

        YOUR ANSWER:
        """

        # 3. Get the answer
        response = model.generate_content(prompt)
        return response.text.strip()
    
    except Exception as e:
        print(f"Error communicating with Gemini: {e}")
        return "I am currently experiencing high traffic. Please try again in a moment."