import re
import csv
import io
import base64
import functools
from textblob import TextBlob
from PIL import Image

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session, flash, Response
from app.extensions import db
from app.email_utils import send_async_email
from app.models import ChatHistory, StudentLead, Appointment
from app.services.gemini_service import get_chat_response, generate_summary, get_vision_response
from app.services.telegram_service import set_telegram_status, get_telegram_status

# --- Global Config ---
bp = Blueprint('main', __name__)
MAINTENANCE_MODE = False

# Image Map for Visual Responses
IMAGE_MAP = {
    "hostel": "https://jecrcuniversity.edu.in/wp-content/uploads/2023/01/9900.webp",
    "room": "https://jecrcuniversity.edu.in/wp-content/uploads/2023/01/9897.webp",
    "library": "https://jecrcuniversity.edu.in/wp-content/uploads/2023/01/Library-1-1.webp",
    "campus": "https://jecrcuniversity.edu.in/wp-content/uploads/2023/01/9845.webp",
    "map": "https://jecrcuniversity.edu.in/wp-content/uploads/2023/06/Drone-Image-JU.png",
    "canteen": "https://jecrcuniversity.edu.in/wp-content/uploads/2025/06/M3_03025-scaled.jpg",
    "event": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRvA_9NkSHIoyR0F5D--0i4ZbhCzG1wI00dEg&s"
}

# --- Auth Helper ---
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if session.get('logged_in') is None:
            return redirect(url_for('main.login'))
        return view(**kwargs)
    return wrapped_view

# ==========================================
# 1. PUBLIC ROUTES (Chat & Booking)
# ==========================================

@bp.route('/')
def home():
    return render_template('index.html', maintenance_mode=MAINTENANCE_MODE)

@bp.route('/api/chat', methods=['POST'])
def chat():
    global MAINTENANCE_MODE
    if MAINTENANCE_MODE:
        return jsonify({'response': "⚠️ **System Maintenance:** Please try again later."})

    data = request.get_json()
    user_message = data.get('message', '')
    image_data = data.get('image')

    if not user_message and not image_data:
        return jsonify({'error': 'No content provided'}), 400

    # --- 1. LEAD CAPTURE ---
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    phone_pattern = r'\b\d{10}\b'
    
    captured = re.search(email_pattern, user_message) or re.search(phone_pattern, user_message)
    if captured:
        try:
            lead_info = captured.group()
            lead = StudentLead(contact_info=lead_info, context=user_message)
            db.session.add(lead)
            db.session.commit()
            
            # Send Email Alert
            send_async_email(f"🎯 New Lead: {lead_info}", f"User asked: {user_message}")
        except Exception as e:
            print(f"Lead Error: {e}")

    # --- 2. AI PROCESSING ---
    bot_response = ""
    if image_data:
        # Vision Mode
        try:
            image_bytes = base64.b64decode(image_data.split(',')[1])
            bot_response = get_vision_response(image_bytes)
        except Exception as e:
            bot_response = "Error processing image."
    else:
        # Text Mode
        bot_response = get_chat_response(user_message)
        
        # Inject Images
        for keyword, image_url in IMAGE_MAP.items():
            if keyword in user_message.lower():
                bot_response += f"""<br><br><img src="{image_url}" class="chat-image" alt="{keyword}">
                <br><span style="font-size:12px; color:#666;">Showing: {keyword.capitalize()}</span>"""
                break

    # --- 3. SENTIMENT ANALYSIS ---
    blob = TextBlob(user_message)
    polarity = blob.sentiment.polarity
    sentiment = "Positive" if polarity > 0.1 else "Negative" if polarity < -0.1 else "Neutral"

    # --- 4. SAVE HISTORY ---
    try:
        chat_entry = ChatHistory(
            user_message="[Image Upload]" if image_data else user_message, 
            bot_response=bot_response,
            sentiment=sentiment
        )
        db.session.add(chat_entry)
        db.session.commit()
        return jsonify({'response': bot_response, 'chat_id': chat_entry.id})
    except Exception as e:
        print(f"DB Error: {e}")
        return jsonify({'response': bot_response, 'chat_id': None})

@bp.route('/api/feedback', methods=['POST'])
def feedback():
    data = request.get_json()
    chat = ChatHistory.query.get(data.get('chat_id'))
    if chat:
        chat.rating = data.get('rating')
        db.session.commit()
        return jsonify({'status': 'success'})
    return jsonify({'error': 'Invalid request'}), 400

@bp.route('/booking', methods=['GET', 'POST'])
def booking():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        visit_date = request.form.get('visit_date')
        purpose = request.form.get('purpose')

        if name and email and visit_date:
            try:
                new_appt = Appointment(name=name, email=email, visit_date=visit_date, purpose=purpose)
                db.session.add(new_appt)
                db.session.commit()
                flash('✅ Appointment booked successfully!', 'success')
                return redirect(url_for('main.home'))
            except:
                flash('❌ Error: Could not save appointment.', 'error')
        else:
            flash('Please fill out all required fields.', 'error')
    return render_template('booking_form.html')

# ==========================================
# 2. AUTHENTICATION
# ==========================================

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('password') == 'admin123':
            session['logged_in'] = True
            return redirect(url_for('main.admin_panel'))
        else:
            flash('Invalid password')
    return render_template('login.html')

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.home'))

# ==========================================
# 3. ADMIN PANEL
# ==========================================

@bp.route('/admin')
@login_required
def admin_panel():
    global MAINTENANCE_MODE
    
    # Fetch Data
    chats = ChatHistory.query.order_by(ChatHistory.timestamp.desc()).all()
    leads = StudentLead.query.order_by(StudentLead.timestamp.desc()).all()
    appointments = Appointment.query.order_by(Appointment.timestamp.desc()).all()
    telegram_status = get_telegram_status()

    # Analytics
    total = ChatHistory.query.count()
    pos = ChatHistory.query.filter_by(rating=1).count()
    neg = ChatHistory.query.filter_by(rating=-1).count()
    
    stats = {
        'total_chats': total, 
        'total_leads': StudentLead.query.count(),
        'positive': pos, 
        'negative': neg, 
        'neutral': total - (pos+neg)
    }

    return render_template('admin.html', 
                           chats=chats, 
                           leads=leads, 
                           appointments=appointments,
                           stats=stats, 
                           maintenance_mode=MAINTENANCE_MODE,
                           telegram_status=telegram_status)

# --- Admin Actions ---

@bp.route('/admin/toggle_maintenance', methods=['POST'])
@login_required
def toggle_maintenance():
    global MAINTENANCE_MODE
    MAINTENANCE_MODE = not MAINTENANCE_MODE
    status = "Maintenance Mode ON" if MAINTENANCE_MODE else "System Online"
    flash(f"Status changed: {status}", 'info')
    return redirect(url_for('main.admin_panel'))

@bp.route('/admin/toggle_telegram', methods=['POST'])
@login_required
def toggle_telegram():
    new_status = not get_telegram_status()
    set_telegram_status(new_status)
    msg = "🟢 Telegram Bot Online" if new_status else "🔴 Telegram Bot Paused"
    flash(msg, 'info')
    return redirect(url_for('main.admin_panel'))

@bp.route('/admin/summarize_chat/<int:chat_id>', methods=['POST'])
@login_required
def summarize_chat_route(chat_id):
    chat = ChatHistory.query.get(chat_id)
    if chat:
        chat.summary = generate_summary(chat.user_message, chat.bot_response)
        db.session.commit()
        return jsonify({'status': 'success', 'summary': chat.summary})
    return jsonify({'error': 'Not found'}), 404

# --- Deletion Routes ---

@bp.route('/admin/clear', methods=['POST'])
@login_required
def clear_history():
    db.session.query(ChatHistory).delete()
    db.session.commit()
    return redirect(url_for('main.admin_panel'))

@bp.route('/admin/clear_leads', methods=['POST'])
@login_required
def clear_leads():
    db.session.query(StudentLead).delete()
    db.session.commit()
    return redirect(url_for('main.admin_panel'))

@bp.route('/admin/delete_appointment/<int:appt_id>', methods=['POST'])
@login_required
def delete_appointment(appt_id):
    try:
        appt = Appointment.query.get(appt_id)
        if appt:
            db.session.delete(appt)
            db.session.commit()
            flash('Appointment cancelled.', 'success')
    except:
        db.session.rollback()
    return redirect(url_for('main.admin_panel'))

# --- Export Routes ---

@bp.route('/admin/export_leads')
@login_required
def export_leads():
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Timestamp', 'Contact', 'Context'])
    for l in StudentLead.query.all():
        writer.writerow([l.id, l.timestamp, l.contact_info, l.context])
    return Response(output.getvalue(), mimetype="text/csv", headers={"Content-disposition": "attachment; filename=leads.csv"})

@bp.route('/admin/export_chats')
@login_required
def export_chats():
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Timestamp', 'User', 'Bot', 'Sentiment', 'Rating'])
    for c in ChatHistory.query.all():
        writer.writerow([c.id, c.timestamp, c.user_message, c.bot_response, c.sentiment, c.rating])
    return Response(output.getvalue(), mimetype="text/csv", headers={"Content-disposition": "attachment; filename=chats.csv"})