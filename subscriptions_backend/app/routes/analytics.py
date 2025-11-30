from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

bp = Blueprint('analytics', __name__)

from app.services.analytics_engine import AnalyticsEngine
from flask_jwt_extended import get_jwt_identity

@bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard():
    user_id = get_jwt_identity()
    engine = AnalyticsEngine()
    recommendations = engine.get_recommendations(user_id)
    
    return jsonify({
        'recommendations': recommendations
    }), 200
