from app import create_app
from app.extensions import db  # <--- Import from extensions

app = create_app()

with app.app_context():
    # Import models so SQLAlchemy knows what to create
    from app.models import ChatHistory
    
    db.create_all()
    print("✅ Database tables created successfully!")