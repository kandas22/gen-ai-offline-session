from app import db
from datetime import datetime
import uuid
from sqlalchemy.dialects.postgresql import UUID

class Subscription(db.Model):
    __tablename__ = 'subscriptions'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=True)
    cost = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), default='USD')
    billing_cycle = db.Column(db.String(20), default='monthly') # monthly, yearly
    start_date = db.Column(db.Date, nullable=True)
    renewal_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(20), default='active') # active, cancelled, paused
    auto_detected = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    usage_logs = db.relationship('UsageLog', backref='subscription', lazy=True)

    def to_dict(self):
        return {
            'id': str(self.id),
            'user_id': str(self.user_id),
            'name': self.name,
            'category': self.category,
            'cost': self.cost,
            'currency': self.currency,
            'billing_cycle': self.billing_cycle,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'renewal_date': self.renewal_date.isoformat() if self.renewal_date else None,
            'status': self.status,
            'auto_detected': self.auto_detected
        }
