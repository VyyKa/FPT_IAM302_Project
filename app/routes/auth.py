from flask import Blueprint, request, jsonify, session
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, unset_jwt_cookies
from app.models import User
from app import db
from app.utils.response_utils import response_dict
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/signin', methods=['POST'])
def signin():
    data = request.get_json()

    if not data or 'username' not in data or 'password' not in data:
        return jsonify(response_dict('error', 'Username and password are required', {})), 400

    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        return jsonify(response_dict('success', 'Login successful', {
            'access_token': access_token,
            'refresh_token': refresh_token
        })), 200
    return jsonify(response_dict('error', 'Invalid username or password', {})), 401

@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()

    if not data or 'username' not in data or 'email' not in data or 'password' not in data:
        return jsonify(response_dict('error', 'Username, email, and password are required', {})), 400

    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if User.query.filter_by(username=username).first():
        return jsonify(response_dict('error', 'Username already exists', {})), 400

    if User.query.filter_by(email=email).first():
        return jsonify(response_dict('error', 'Email already registered', {})), 400

    hashed_password = generate_password_hash(password)
    new_user = User(username=username, email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify(response_dict('success', 'User created successfully', {})), 201

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    response = jsonify(response_dict('success', 'Logged out successfully', {}))
    unset_jwt_cookies(response)
    session.clear()  # Clear the session
    return response, 200