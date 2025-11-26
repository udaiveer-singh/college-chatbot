from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from app.services.gemini_service import get_chat_response
from app.extensions import db
from app.models import ChatHistory

bp = Blueprint('main', __name__)

# --- EXISTING ROUTES ---
@bp.route('/')
def home():
    return render_template('index.html')

@bp.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message', '')
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400

    # Get Response & Save
    bot_response = get_chat_response(user_message)
    try:
        chat_entry = ChatHistory(user_message=user_message, bot_response=bot_response)
        db.session.add(chat_entry)
        db.session.commit()
    except Exception as e:
        print(f"Error saving to DB: {e}")

    return jsonify({'response': bot_response})

# --- NEW ADMIN ROUTES ---

@bp.route('/admin')
def admin_panel():
    """
    Displays the admin dashboard with all chat logs.
    """
    # Get all chats, sorted by newest first (descending order)
    chats = ChatHistory.query.order_by(ChatHistory.timestamp.desc()).all()
    return render_template('admin.html', chats=chats)

@bp.route('/admin/clear', methods=['POST'])
def clear_history():
    """
    Deletes all records from the database.
    """
    try:
        db.session.query(ChatHistory).delete()
        db.session.commit()
    except Exception as e:
        print(f"Error clearing DB: {e}")
        db.session.rollback()
    
    return redirect(url_for('main.admin_panel'))