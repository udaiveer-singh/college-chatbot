import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from app.services.gemini_service import get_chat_response
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Global Toggle Flag
# CHANGED: Default to true so it works immediately for testing
IS_TELEGRAM_ACTIVE = True  

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Responds to /start command."""
    print(f"📩 Telegram: Received /start from {update.effective_user.first_name}")
    
    if not IS_TELEGRAM_ACTIVE:
        await update.message.reply_text("🔴 The bot is currently sleeping. An Admin needs to wake me up!")
        return
    await update.message.reply_text("🟢 I am Online! Ask me anything about JECRC University.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles text messages."""
    user_text = update.message.text
    user_name = update.effective_user.first_name
    
    print(f"📩 Telegram Message from {user_name}: {user_text}")

    if not IS_TELEGRAM_ACTIVE:
        print("   -> Ignored (Bot is Paused)")
        # Optional: Uncomment next line to tell user it's off
        await update.message.reply_text("🔴 System is currently paused by Admin.") 
        return

    chat_id = update.effective_chat.id

    # Show typing status
    await context.bot.send_chat_action(chat_id=chat_id, action="typing")

    try:
        # Get AI response
        response = get_chat_response(user_text)
        print(f"   -> Replying: {response[:50]}...")
        
        # Send back (Escape special chars if needed, or simple replace)
        await update.message.reply_text(response.replace('**', '*'))
    except Exception as e:
        print(f"❌ Telegram Error: {e}")
        await update.message.reply_text("Sorry, I had a glitch.")

def run_telegram_bot():
    """Starts the bot polling loop."""
    if not TOKEN:
        print("❌ Telegram Token not found in .env!")
        return

    # Create App
    application = Application.builder().token(TOKEN).build()

    # Add Handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print(f"🤖 Telegram Service Initialized (Active: {IS_TELEGRAM_ACTIVE})")
    
    # Run loop (Note: run.py already sets the loop, so we just poll)
    # application.run_polling(stop_signals=None) for render compatibility
    application.run_polling()

# Helper to toggle status from Routes
def set_telegram_status(status):
    global IS_TELEGRAM_ACTIVE
    print("called set_telegram_status")
    IS_TELEGRAM_ACTIVE = status
    return IS_TELEGRAM_ACTIVE

def get_telegram_status():
    return IS_TELEGRAM_ACTIVE