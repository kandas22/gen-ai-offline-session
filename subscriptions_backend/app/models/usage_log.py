from app import db
from datetime import datetime
import uuid
from sqlalchemy.dialects.postgresql import UUID, JSONB

class UsageLog(db.Model):
    __tablename__ = 'usage_logs'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    subscription_id = db.Column(UUID(as_uuid=True), db.ForeignKey('subscriptions.id'), nullable=False)
    usage_date = db.Column(db.DateTime, default=datetime.utcnow)
    usage_type = db.Column(db.String(50), nullable=True) # login, watch, listen
    duration_minutes = db.Column(db.Integer, nullable=True)
    source = db.Column(db.String(20), default='manual') # email, manual, api
    log_metadata = db.Column(JSONB, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': str(self.id),
            'subscription_id': str(self.subscription_id),
            'usage_date': self.usage_date.isoformat(),
            'usage_type': self.usage_type,
            'duration_minutes': self.duration_minutes,
            'source': self.source,
            'metadata': self.log_metadata
        }
