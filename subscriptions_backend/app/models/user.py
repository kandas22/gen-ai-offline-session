from app import db
from datetime import datetime
import uuid
from sqlalchemy.dialects.postgresql import UUID

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=True) # Optional if using only OAuth
    gmail_token = db.Column(db.Text, nullable=True) # Encrypted token
    gmail_refresh_token = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    subscriptions = db.relationship('Subscription', backref='user', lazy=True)

    def to_dict(self):
        return {
            'id': str(self.id),
            'email': self.email,
            'created_at': self.created_at.isoformat()
        }
