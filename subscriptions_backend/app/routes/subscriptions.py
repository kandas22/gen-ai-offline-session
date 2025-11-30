from flask import Blueprint, request, jsonify
from app import db
from app.models.subscription import Subscription
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

bp = Blueprint('subscriptions', __name__)

@bp.route('/', methods=['GET'])
@jwt_required()
def get_subscriptions():
    current_user_id = get_jwt_identity()
    subscriptions = Subscription.query.filter_by(user_id=current_user_id).all()
    return jsonify([sub.to_dict() for sub in subscriptions]), 200

@bp.route('/', methods=['POST'])
@jwt_required()
def create_subscription():
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    new_sub = Subscription(
        user_id=current_user_id,
        name=data['name'],
        cost=data['cost'],
        category=data.get('category'),
        billing_cycle=data.get('billing_cycle', 'monthly'),
        start_date=datetime.fromisoformat(data['start_date']) if data.get('start_date') else None
    )
    
    db.session.add(new_sub)
    db.session.commit()
    
    return jsonify(new_sub.to_dict()), 201
