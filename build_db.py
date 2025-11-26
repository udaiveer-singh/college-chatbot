from app.services.rag_service import create_vector_db
from dotenv import load_dotenv

load_dotenv() # Load API keys
create_vector_db()