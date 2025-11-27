import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from app.services.gemini_service import get_chat_response
from dotenv import load_dotenv

# Load credentials
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN not found in environment variables.")

# --- 1. CORE HANDLER ---
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Processes incoming text messages and sends them to the Gemini service."""
    if update.message is None or update.message.text is None:
        return

    user_message = update.message.text
    chat_id = update.effective_chat.id

    # Add typing indicator to Telegram chat
    await context.bot.send_chat_action(chat_id=chat_id, action="typing")

    # --- REUSE YOUR EXISTING AI LOGIC ---
    # This is the power of the service-oriented architecture!
    ai_response = get_chat_response(user_message) 

    # Clean up markdown for better display on Telegram
    clean_response = ai_response.replace('**', '*') 
    
    await update.message.reply_text(clean_response)


# --- 2. START COMMAND ---
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a welcome message when the user starts the bot."""
    welcome_message = "Hello! I am the JECRC University AI Assistant. Send me your questions about fees, admissions, or campus life."
    await update.message.reply_text(welcome_message)


# --- 3. MAIN RUNNER ---
def main() -> None:
    """Starts the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    print("🤖 Telegram Bot is running... Press Ctrl+C to stop.")
    
    # Run the bot until the user presses Ctrl-C
    application.run_polling(poll_interval=3)

if __name__ == '__main__':
    main()