import io
import PIL.Image
import os
import google.generativeai as genai
from dotenv import load_dotenv
from app.services.rag_service import get_relevant_context

load_dotenv()

GEN_AI_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GEN_AI_KEY)

# Initialize Gemini 2.0 Flash
model = genai.GenerativeModel(model_name="gemini-2.0-flash")

def get_chat_response(user_message):
    try:
        # 1. Get facts from your PDF
        context = get_relevant_context(user_message)
        
        # 2. The Simple Hybrid Prompt
        prompt = f"""
        You are the AI Assistant for JECRC University.
        
        RELEVANT INFO FROM DOCUMENTS:
        ---------------------
        {context}
        ---------------------
        
        INSTRUCTIONS:
        1. **College Questions:** If the user asks about JECRC (Fees, Courses, Campus), answer ONLY using the "RELEVANT INFO" above. 
           - If the answer is missing in the documents, politely say you don't have that info.
        
        2. **General Questions:** If the user asks about the world (e.g., "What is Python?", "Who is Elon Musk?"), answer helpfuly using your own general knowledge.

        3. **Appointment Booking (NEW):** If the user asks to **book, schedule, or visit the campus/counselor**, you MUST provide this link: 
           - Link: http://127.0.0.1:5000/booking
           - Message: "Yes, you can easily book a slot online. Please follow this link to schedule your visit: [ http://127.0.0.1:5000/booking ]"
           
        4. **Admissions:** If the user asks "How to apply?", kindly ask for their Email ID or Phone Number.
        
        User Question: "{user_message}"
        """

        # 3. Get Answer
        response = model.generate_content(prompt)
        return response.text.strip()
    
    except Exception as e:
        print(f"Error: {e}")
        return "I'm having trouble connecting right now."
    
def generate_summary(user_text, bot_text):
    """
    Uses Gemini to create a 1-sentence summary of the conversation.
    """
    try:
        prompt = f"""
        Summarize the following interaction between a Student and an AI Assistant.
        
        Student: "{user_text}"
        AI: "{bot_text}"
        
        INSTRUCTIONS:
        - Write a concise, professional summary (max 15 words).
        - Focus on the Student's intent (what they wanted).
        - Example: "Student asked about B.Tech fees and hostel availability."
        """
        
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return "Summary unavailable."

def get_vision_response(image_bytes):
    """
    Analyzes an image using Gemini Pro Vision.
    """
    try:
        # Load the image
        img = PIL.Image.open(io.BytesIO(image_bytes))
        
        prompt = """
        Analyze this image. It is likely a student's marksheet or document.
        1. Read the text/numbers visible.
        2. If it's a marksheet, calculate the approximate percentage.
        3. Tell the student if they meet the eligibility criteria (Minimum 60% for B.Tech).
        4. If it's not a document, describe what you see.
        """
        
        # Send Prompt + Image to Gemini
        response = model.generate_content([prompt, img])
        return response.text.strip()
    
    except Exception as e:
        print(f"Vision Error: {e}")
        return "I had trouble analyzing that image. Please ensure it is clear and try again."