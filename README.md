# 🎓 JECRC University AI Assistant  
### *A Next-Gen Multi-Channel AI Chatbot powered by Google Gemini 2.0 Flash, RAG & Computer Vision*

## 🌟 Overview

This is not just a chatbot; it is a complete **AI Ecosystem** designed for JECRC University. It serves as a 24/7 admission counselor, campus guide, and student assistant.

Unlike basic bots, it features a **Dual-Brain Architecture**:

1. **College Expert:** Uses **RAG (Retrieval-Augmented Generation)** to fetch precise answers from official university PDFs (Fees, Syllabus, Hostels).  
2. **General Intelligence:** Uses **Google Gemini** to handle general queries (Coding, Math, World Facts).

---

## ✨ Key Features

### 🧠 Intelligent Core
- Context-Aware RAG (FAISS + LangChain)  
- Multimodal Vision  
- Sentiment Analysis  
- Multilingual Support  

### 💻 Modern Web Interface
- Glassmorphism UI  
- Voice Input & TTS  
- Smart Suggestions  
- Dark Mode  

### 📱 Multi-Channel
- Telegram Bot Integration  
- Admin Bot Toggle  

### ⚙️ Admin Dashboard
- Lead Generation  
- Real-Time Alerts  
- Analytics with Chart.js  
- Appointment Booking  
- AI Chat Summaries  

---

## 🛠️ Technology Stack

| Component | Technology |
|----------|------------|
| Backend | Python (Flask), Gunicorn |
| AI Engine | Google Gemini 2.0 Flash |
| Vector DB | FAISS |
| Orchestration | LangChain |
| Database | SQLite |
| Frontend | HTML, CSS (Glassmorphism), JS |
| Integrations | Telegram API, SMTP |

---

## 📂 Project Structure

```text
college_chatbot/
├── app/
│   ├── services/
│   ├── static/
│   ├── templates/
│   ├── models.py
│   ├── routes.py
│   ├── email_utils.py
│   ├── __init__.py
├── data/
│   └── documents/
├── instance/
│   ├── chatbot.db
│   └── faiss_index/
├── build_db.py
├── create_tables.py
├── run.py
├── requirements.txt
└── .env
```

---

## 🚀 Installation & Setup

```bash
git clone https://github.com/your-username/college-chatbot.git
cd college-chatbot
pip install -r requirements.txt
```

Configure `.env`:

```ini
GOOGLE_API_KEY=your_api_key
SECRET_KEY=random_key
DATABASE_URL=sqlite:///chatbot.db
TELEGRAM_BOT_TOKEN=your_bot_token
MAIL_SENDER=email
MAIL_PASSWORD=app_password
MAIL_RECEIVER=admin_email
```

Build RAG DB:

```bash
python build_db.py
python create_tables.py
python run.py
```

---

## 🤝 Contribution

Pull requests are welcome!

**Made with ❤️ for JECRC University.**
