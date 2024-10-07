from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User, UploadedFile
from app.utils.response_utils import response_dict

user_bp = Blueprint('user_bp', __name__)

@user_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify(response_dict('error', 'User not found', {})), 404

    user_data = {
        'id': user.id,
        'username': user.username,
        'email': user.email
    }

    return jsonify(response_dict('success', 'User profile retrieved', {'user': user_data})), 200

@user_bp.route('/files', methods=['GET'])
@jwt_required()
def get_user_files():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify(response_dict('error', 'User not found', {})), 404

    files = UploadedFile.query.filter_by(user_id=user_id).all()
    files_data = [{
        'filename': file.filename,
        'status': file.status,
        'timestamp': file.timestamp
    } for file in files]

    return jsonify(response_dict('success', 'User files retrieved', {'files': files_data})), 200