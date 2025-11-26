import os
import time
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Setup Embeddings
# We use 'models/text-embedding-004' which is newer and often has better rate limits
embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")

DB_FAISS_PATH = "instance/faiss_index"
DATA_PATH = "data/documents"

def create_vector_db():
    """
    Reads PDFs, splits them, and saves a searchable index.
    Includes rate-limit handling for Free Tier users.
    """
    if not os.path.exists(DATA_PATH):
        os.makedirs(DATA_PATH)
        print(f"⚠️ No documents found in {DATA_PATH}. Please add PDFs.")
        return

    print("Loading PDFs...")
    loader = PyPDFDirectoryLoader(DATA_PATH)
    documents = loader.load()

    if not documents:
        print("❌ No PDF files found. Add a file to data/documents/ first.")
        return

    print(f"Processing {len(documents)} pages...")
    
    # Split text into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    texts = text_splitter.split_documents(documents)
    
    total_chunks = len(texts)
    print(f"Total chunks to process: {total_chunks}")
    print("Starting batch embedding (this will take time to avoid rate limits)...")

    # --- BATCH PROCESSING LOGIC ---
    batch_size = 10  # Process only 10 chunks at a time
    vector_db = None

    for i in range(0, total_chunks, batch_size):
        batch = texts[i : i + batch_size]
        print(f"  - Embedding batch {i//batch_size + 1} / {(total_chunks // batch_size) + 1}...")
        
        try:
            if vector_db is None:
                # First batch creates the DB
                vector_db = FAISS.from_documents(batch, embeddings)
            else:
                # Subsequent batches are added to the existing DB
                vector_db.add_documents(batch)
            
            # CRITICAL: Sleep to respect Google's Free Tier limits
            time.sleep(3) 

        except Exception as e:
            print(f"❌ Error on batch {i}: {e}")
            # Wait longer if we hit an error, then try to continue
            time.sleep(10)

    # Save locally
    if vector_db:
        vector_db.save_local(DB_FAISS_PATH)
        print("✅ Knowledge Base Ready!")
    else:
        print("❌ Failed to create database.")

def get_relevant_context(query):
    """
    Searches the database for text related to the user's question.
    """
    if not os.path.exists(DB_FAISS_PATH):
        return "" 

    vector_db = FAISS.load_local(DB_FAISS_PATH, embeddings, allow_dangerous_deserialization=True)
    docs = vector_db.similarity_search(query, k=3)
    context = "\n".join([doc.page_content for doc in docs])
    return context