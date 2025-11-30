from app.models.subscription import Subscription
from app.models.usage_log import UsageLog
from datetime import datetime, timedelta

class AnalyticsEngine:
    def calculate_effectiveness(self, subscription_id):
        # Example logic:
        # Score = (Usage Count / Expected Usage) * 100
        # Expected Usage could be 1 per day for streaming, etc.
        
        sub = Subscription.query.get(subscription_id)
        if not sub:
            return 0
            
        # Get usage for last 30 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        usage_count = UsageLog.query.filter(
            UsageLog.subscription_id == subscription_id,
            UsageLog.usage_date >= thirty_days_ago
        ).count()
        
        # Define expected usage based on category (simplified)
        expected_usage = 10 # Default
        if sub.category == 'streaming':
            expected_usage = 15 # Every other day
        elif sub.category == 'music':
            expected_usage = 20
            
        score = min((usage_count / expected_usage) * 100, 100)
        return round(score, 2)

    def get_recommendations(self, user_id):
        subs = Subscription.query.filter_by(user_id=user_id).all()
        recommendations = []
        
        for sub in subs:
            score = self.calculate_effectiveness(sub.id)
            if score < 30:
                recommendations.append({
                    'subscription': sub.name,
                    'action': 'cancel',
                    'reason': f'Low usage ({score}% effectiveness)',
                    'potential_savings': sub.cost
                })
                
        return recommendations
