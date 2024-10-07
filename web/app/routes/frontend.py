# app/routes/frontend.py

from flask import Blueprint, render_template, session

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