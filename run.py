import os
import threading
import asyncio
from app import create_app
from app.extensions import db
from app.services.telegram_service import run_telegram_bot

# 1. Initialize the Flask Application
app = create_app()

# 2. AUTOMATIC DATABASE CREATION
# This fixes the "Login page stopped" or "Missing Tables" issue on Render.
# It runs every time the app starts to ensure tables exist.
with app.app_context():
    try:
        db.create_all()
        print("✅ Database tables checked/created successfully.")
    except Exception as e:
        print(f"❌ Error creating database tables: {e}")

# 3. BACKGROUND SERVICE: TELEGRAM BOT
def start_background_services():
    """
    Runs the Telegram Bot in a separate thread so it doesn't block the website.
    """
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    
    if not token:
        print("⚠️ No TELEGRAM_BOT_TOKEN found in .env. Telegram Bot will NOT start.")
        return

    print("🤖 Starting Telegram Bot service...")
    
    # Critical: Create a new asyncio loop for this thread
    # (Telegram library requires asyncio, which is sensitive to threads)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # Start the bot logic
    run_telegram_bot()

# 4. LAUNCH THREAD
# We run this check to ensure the thread starts whether you use 
# 'python run.py' (Local) OR 'gunicorn run:app' (Render)
if os.environ.get("WERKZEUG_RUN_MAIN") != "true": 
    # This weird check prevents the bot from starting twice in Flask Debug mode
    tg_thread = threading.Thread(target=start_background_services)
    tg_thread.daemon = True # Ensures thread dies if the main app crashes
    tg_thread.start()

# 5. START SERVER (Local Development Only)
if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)