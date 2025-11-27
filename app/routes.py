from app.models import ChatHistory, StudentLead, Appointment # <--- Add Appointment
from flask import render_template, request, jsonify, redirect, url_for, session, flash # <--- Ensure flash is imported
import base64
import io
from PIL import Image
from app.services.gemini_service import get_chat_response, generate_summary, get_vision_response
import csv
import io
from flask import Response # Add Response to your imports
from app.email_utils import send_async_email
from textblob import TextBlob
import re
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session, flash
from app.services.gemini_service import get_chat_response
from app.extensions import db
import functools
from app.models import ChatHistory, StudentLead

bp = Blueprint('main', __name__)
# Global Maintenance Flag (False = Online, True = Maintenance)
MAINTENANCE_MODE = False

# --- 1. DEFINE YOUR IMAGES HERE ---
# (You can replace these URLs with actual links to JECRC images later)
IMAGE_MAP = {
    "hostel": "https://jecrcuniversity.edu.in/wp-content/uploads/2023/01/9900.webp",
    "room": "https://jecrcuniversity.edu.in/wp-content/uploads/2023/01/9897.webp",
    "library": "https://jecrcuniversity.edu.in/wp-content/uploads/2023/01/Library-1-1.webp",
    "campus": "https://jecrcuniversity.edu.in/wp-content/uploads/2023/01/9845.webp",
    "map": "https://jecrcuniversity.edu.in/wp-content/uploads/2023/06/Drone-Image-JU.png",
    "canteen": "https://jecrcuniversity.edu.in/wp-content/uploads/2025/06/M3_03025-scaled.jpg",
    "event": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRvA_9NkSHIoyR0F5D--0i4ZbhCzG1wI00dEg&s"
}

# --- Helper: Login Required Decorator ---
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if session.get('logged_in') is None:
            return redirect(url_for('main.login'))
        return view(**kwargs)
    return wrapped_view

# --- PUBLIC ROUTES ---

@bp.route('/')
def home():
    return render_template('index.html', maintenance_mode=MAINTENANCE_MODE)

@bp.route('/api/chat', methods=['POST'])
def chat():
    # 1. Check Maintenance Mode
    global MAINTENANCE_MODE
    if MAINTENANCE_MODE:
        return jsonify({'response': "⚠️ **System Maintenance:** The chatbot is currently being updated. Please check back after a while."})
    data = request.get_json()
    user_message = data.get('message', '')
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400
    image_data = data.get('image')

    # --- NEW: LEAD DETECTION LOGIC ---
    # Regex to find an Email Address
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    # Regex to find a 10-digit Phone Number
    phone_pattern = r'\b\d{10}\b'

    # 1. Capture Leads (Regex)
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    phone_pattern = r'\b\d{10}\b'
    
    captured = re.search(email_pattern, user_message) or re.search(phone_pattern, user_message)

    if captured:
        try:
            lead_info = captured.group()
            lead = StudentLead(contact_info=lead_info, context="Chat Lead")
            db.session.add(lead)
            db.session.commit()
            
            # --- NEW: SEND EMAIL ALERT ---
            subject = f"🎯 New Student Lead: {lead_info}"
            body = f"""
            Hello Admin,

            A new student lead was just captured by the JECRC Bot.

            📞 Contact: {lead_info}
            💬 Context: User asked about "{user_message}"
            
            Check the dashboard for details: http://127.0.0.1:5000/admin
            """
            send_async_email(subject, body)
            # -----------------------------

        except Exception as e:
            print(f"Error processing lead: {e}")
    
    # 2. NEW: Sentiment Analysis
    blob = TextBlob(user_message)
    polarity = blob.sentiment.polarity # Score between -1 (Negative) and +1 (Positive)
    
    sentiment = "Neutral"
    if polarity > 0.1:
        sentiment = "Positive"
    elif polarity < -0.1:
        sentiment = "Negative"
        
    # 2. AI Processing
    bot_response = ""
    
    if image_data:
        # --- VISION MODE ---
        try:
            # Decode base64 to bytes
            image_bytes = base64.b64decode(image_data.split(',')[1])
            # Call the service function (No 'model' error now!)
            bot_response = get_vision_response(image_bytes)
        except Exception as e:
            print(f"Image Error: {e}")
            bot_response = "Error processing image."
            
    else:
        # --- TEXT MODE ---
        bot_response = get_chat_response(user_message)
    
    # 3. --- NEW: INJECT IMAGES ---
    # Check if the user message contains any keywords from our map
    msg_lower = user_message.lower()
    for keyword, image_url in IMAGE_MAP.items():
        if keyword in msg_lower:
            # Append an HTML image tag to the response
            bot_response += f"""
            <br><br>
            <img src="{image_url}" class="chat-image" alt="{keyword}">
            <br><span style="font-size:12px; color:#666;">Showing: {keyword.capitalize()}</span>
            """
            break # Stop after finding the first relevant image
    
    # Save Chat History
    try:
        chat_entry = ChatHistory(user_message=user_message, bot_response=bot_response,sentiment=sentiment)
        if image_data:
            chat_entry.user_message = "[User Uploaded an Image]" # Placeholder for DB
        db.session.add(chat_entry)
        db.session.commit()
    except Exception as e:
        print(f"Error saving chat: {e}")

    return jsonify({
        'response': bot_response,
        'chat_id': chat_entry.id  
    })
    
@bp.route('/api/feedback', methods=['POST'])
def feedback():
    data = request.get_json()
    chat_id = data.get('chat_id')
    rating = data.get('rating') # 1 (Like) or -1 (Dislike)

    if chat_id:
        chat = ChatHistory.query.get(chat_id)
        if chat:
            chat.rating = rating
            db.session.commit()
            return jsonify({'status': 'success'})
    
    return jsonify({'error': 'Invalid request'}), 400

# --- AUTH ROUTES ---
@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        # Simple password check (In real app, use Hash)
        if password == 'admin123':
            session['logged_in'] = True
            return redirect(url_for('main.admin_panel'))
        else:
            flash('Invalid password')
    return render_template('login.html')

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.home'))

# --- ADMIN ROUTES (Protected) ---

@bp.route('/admin')
@login_required
def admin_panel():
    global MAINTENANCE_MODE # Access the variable
    # 1. Fetch Data
    chats = ChatHistory.query.order_by(ChatHistory.timestamp.desc()).all()
    leads = StudentLead.query.order_by(StudentLead.timestamp.desc()).all()
    appointments = Appointment.query.order_by(Appointment.timestamp.desc()).all()

    # 2. Calculate Analytics
    total_chats = ChatHistory.query.count()
    total_leads = StudentLead.query.count()
    
    positive_feedback = ChatHistory.query.filter_by(rating=1).count()
    negative_feedback = ChatHistory.query.filter_by(rating=-1).count()
    neutral_feedback = total_chats - (positive_feedback + negative_feedback)

    # 3. Pack data into a dictionary
    stats = {
        'total_chats': total_chats,
        'total_leads': total_leads,
        'positive': positive_feedback,
        'negative': negative_feedback,
        'neutral': neutral_feedback
    }

    # Pass 'maintenance_status' to the template
    return render_template('admin.html', 
                           chats=chats, 
                           leads=leads, 
                           stats=stats, 
                           appointments=appointments,
                           maintenance_mode=MAINTENANCE_MODE)

@bp.route('/admin/clear', methods=['POST'])
@login_required
def clear_history():
    try:
        db.session.query(ChatHistory).delete()
        db.session.commit()
    except Exception as e:
        print(f"Error: {e}")
        db.session.rollback()
    return redirect(url_for('main.admin_panel'))

@bp.route('/admin/clear_leads', methods=['POST'])
@login_required
def clear_leads():
    """
    Deletes all student leads from the database.
    """
    try:
        db.session.query(StudentLead).delete()
        db.session.commit()
        flash('All leads have been deleted.', 'success')
    except Exception as e:
        print(f"Error clearing leads: {e}")
        db.session.rollback()
        flash('Error deleting leads.', 'error')
    
    return redirect(url_for('main.admin_panel'))
@bp.route('/booking', methods=['GET', 'POST'])
def booking():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        visit_date = request.form.get('visit_date')
        purpose = request.form.get('purpose')

        if name and email and visit_date:
            try:
                # Save Appointment to DB
                new_appt = Appointment(
                    name=name,
                    email=email,
                    visit_date=visit_date,
                    purpose=purpose
                )
                db.session.add(new_appt)
                db.session.commit()
                flash('✅ Appointment booked successfully! We look forward to seeing you.', 'success')
                
                # Optional: Send email confirmation to user/admin here
                return redirect(url_for('main.home'))
            except Exception as e:
                print(f"Booking Error: {e}")
                flash('❌ Error: Could not save appointment. Please check your input.', 'error')
        else:
            flash('Please fill out all required fields.', 'error')

    return render_template('booking_form.html')

@bp.route('/admin/appointments')
@login_required
def appointments_panel():
    appointments = Appointment.query.order_by(Appointment.timestamp.desc()).all()
    return render_template('admin_appointments.html', appointments=appointments)
@bp.route('/admin/toggle_maintenance', methods=['POST'])
@login_required
def toggle_maintenance():
    global MAINTENANCE_MODE
    MAINTENANCE_MODE = not MAINTENANCE_MODE # Flip the switch

    status = "Maintenance Mode ON" if MAINTENANCE_MODE else "System Online"
    flash(f"Status changed: {status}", 'info')

    return redirect(url_for('main.admin_panel'))
@bp.route('/admin/export_leads')
@login_required
def export_leads():
    """
    Generates a CSV file of all student leads.
    """
    leads = StudentLead.query.all()
    
    # Create an in-memory CSV file
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write Header
    writer.writerow(['ID', 'Timestamp', 'Contact Info', 'Context'])
    
    # Write Rows
    for lead in leads:
        writer.writerow([lead.id, lead.timestamp, lead.contact_info, lead.context])
        
    output.seek(0)
    
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=student_leads.csv"}
    )

@bp.route('/admin/export_chats')
@login_required
def export_chats():
    """
    Generates a CSV file of all chat history.
    """
    chats = ChatHistory.query.all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write Header
    writer.writerow(['ID', 'Timestamp', 'User Message', 'Bot Response', 'Sentiment', 'Rating'])
    
    # Write Rows
    for chat in chats:
        writer.writerow([
            chat.id, 
            chat.timestamp, 
            chat.user_message, 
            chat.bot_response, 
            chat.sentiment,
            chat.rating
        ])
        
    output.seek(0)
    
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=chat_history.csv"}
    )
@bp.route('/admin/summarize_chat/<int:chat_id>', methods=['POST'])
@login_required
def summarize_chat_route(chat_id):
    chat = ChatHistory.query.get(chat_id)
    if chat:
        # Generate Summary
        summary = generate_summary(chat.user_message, chat.bot_response)
        
        # Save to DB
        chat.summary = summary
        db.session.commit()
        
        return jsonify({'status': 'success', 'summary': summary})
    
    return jsonify({'error': 'Chat not found'}), 404

@bp.route('/admin/delete_appointment/<int:appt_id>', methods=['POST'])
@login_required
def delete_appointment(appt_id):
    """
    Cancels (deletes) a specific appointment.
    """
    try:
        appt = Appointment.query.get(appt_id)
        if appt:
            db.session.delete(appt)
            db.session.commit()
            flash('✅ Appointment cancelled successfully.', 'success')
        else:
            flash('❌ Appointment not found.', 'error')
    except Exception as e:
        print(f"Error deleting appointment: {e}")
        db.session.rollback()
        flash('Error cancelling appointment.', 'error')
    
    return redirect(url_for('main.admin_panel'))