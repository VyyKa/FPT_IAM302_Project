# app/routes/frontend.py

from flask import Blueprint, render_template, session
from ..models import UploadedFile, User
import requests

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

@frontend_bp.route('/get_report/<task_id>', methods=['GET'])
def get_report(task_id):
    # Check if the task_id is exists
    UploadedFile.query.filter_by(task_id=task_id).first_or_404()

    # URL of the Cuckoo API to retrieve the report
    report_format = "pdf"
    cuckoo_report_url = f"http://localhost:8000/apiv2/tasks/get/report/{task_id}/{report_format}/"
    # curl apiv2/tasks/get/report/[task id]/[format]/
    try:
        # Send a GET request to retrieve the report from the Cuckoo API
        response = requests.get(cuckoo_report_url)
        
        # Check if the request was successful
        if response.status_code == 200:
            report_file_raw = response.content

            # Return the report file content as a response
            return report_file_raw, 200, {"Content-Type": "application/pdf"}
    except requests.exceptions.RequestException as e:
        return {"error": f"Request to Cuckoo API failed: {str(e)}"}, 500
    
@frontend_bp.route('/get_ml_report/<task_id>', methods=['GET'])
def get_ml_report(task_id):
    # Check if the task_id is exists
    report = UploadedFile.query.filter_by(task_id=task_id).first_or_404()

    # URL of the Machine Learning API to retrieve the report
    ml_report = report.results

    # Return the report file content as a response as text
    return ml_report, 200, {"Content-Type": "text/plain"}