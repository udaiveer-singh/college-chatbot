from datetime import datetime
from app.extensions import db

class ChatHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_message = db.Column(db.Text, nullable=False)
    bot_response = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, default=0)
    sentiment = db.Column(db.String(20), default="Neutral")
    summary = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# NEW TABLE: Store Student Leads
class StudentLead(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contact_info = db.Column(db.String(150), nullable=False) # Email or Phone
    context = db.Column(db.String(200)) # What they were asking about
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    visit_date = db.Column(db.String(50), nullable=False)
    purpose = db.Column(db.String(200), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)