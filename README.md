# 🎓 JECRC University AI Chatbot

A smart, hybrid AI assistant designed for JECRC University. It uses **Retrieval-Augmented Generation (RAG)** to answer specific college queries (Fees, Courses, Hostels) using official documents, while leveraging **Google Gemini 2.0 Flash** for general knowledge.

![Status](https://img.shields.io/badge/Status-Active-success)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Flask](https://img.shields.io/badge/Framework-Flask-green)

## 🚀 Key Features

* **Dual-Brain Architecture:**
    * **Expert Mode:** Answers specific queries using a vector database of college PDFs.
    * **General Mode:** Handles greetings and general knowledge using Gemini AI.
* **Smart Routing:** Automatically detects if a question is about the college or general topics.
* **Admin Dashboard:** A password-protected (concept) panel to view live chat analytics.
* **Chat History:** Saves all conversations to a SQLite database for review.
* **Rate-Limit Handling:** Smart batching logic to handle API limits gracefully.

## 🛠️ Technology Stack

* **Backend:** Flask (Python)
* **AI Engine:** Google Gemini 2.0 Flash
* **Vector Database:** FAISS (Facebook AI Similarity Search)
* **Orchestration:** LangChain
* **Database:** SQLite (SQLAlchemy)
* **Frontend:** HTML5, CSS3, JavaScript (Vanilla)

## ⚙️ Installation & Setup

1.  **Clone the Repository**
    ```bash
    git clone [https://github.com/yourusername/college-chatbot.git](https://github.com/yourusername/college-chatbot.git)
    cd college-chatbot
    ```

2.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure Environment**
    Create a `.env` file in the root directory:
    ```ini
    GOOGLE_API_KEY=your_google_gemini_key
    SECRET_KEY=your_secret_key
    DATABASE_URL=sqlite:///chatbot.db
    ```

4.  **Build the Knowledge Base**
    Place your college PDF in `data/documents/` and run:
    ```bash
    python build_db.py
    ```

5.  **Run the Application**
    ```bash
    python run.py
    ```
    Access the bot at `http://127.0.0.1:5000`

## 📊 Admin Panel
Access the dashboard at `/admin` to view chat logs.