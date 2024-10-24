# app/routes/frontend.py

from flask import Blueprint, render_template, session
from ..models import UploadedFile, User

frontend_bp = Blueprint('frontend', __name__, template_folder='../../templates')

@frontend_bp.route('/')
def index():
    username = session.get('username', None)  # Get the username from session
    return render_template('index.html', username=username)

@frontend_bp.route('/signin')
def signin():
    return render_template('signin.html')

@frontend_bp.route('/signup')
def signup():
    return render_template('signup.html')

@frontend_bp.route('/upload')
def upload():
    return render_template('upload.html')

@frontend_bp.route('/status')
def status():
    user_id = session.get('user_id')  # Get user_id from session
    is_admin = session.get('is_admin', False)  # Check if user is admin

    if is_admin:
        # Admin user: get all files
        all_files = UploadedFile.query.all()
    elif user_id:
        # Regular user: get only their files
        all_files = UploadedFile.query.filter_by(user_id=user_id).all()
    else:
        all_files = []  # No user logged in

    return render_template('status.html', files=all_files)