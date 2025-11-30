from flask import Blueprint, request, jsonify
from app import db
from app.models.usage_log import UsageLog
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

bp = Blueprint('usage', __name__)

@bp.route('/', methods=['GET'])
@jwt_required()
def get_usage():
    # Implement filtering logic here
    usage_logs = UsageLog.query.limit(100).all() # Placeholder
    return jsonify([log.to_dict() for log in usage_logs]), 200
