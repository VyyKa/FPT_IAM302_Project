from flask import Blueprint, request, jsonify
from app.models import UploadedFile
from app import db
import requests

callback_bp = Blueprint('callback_bp', __name__)

@callback_bp.route('/callback', methods=['POST'])
def callback():
    # Get JSON data from the request
    data = request.get_json()
    if not data or 'task_id' not in data:
        return jsonify({"error": "task_id is required"}), 400
    
    task_id = data.get('task_id')
    detection = data.get('detection', 'Unknown')
    status = data.get('status', 'Unknown')

    # Check if the task failed
    if status != "success":
        # Update status to 'Failed' in the database
        UploadedFile.query.filter_by(task_id=task_id).update({'status': 'Failed'})
        db.session.commit()
        return jsonify({"task_id": task_id, "status": "Failed"}), 200

    # If the task succeeded, update the detection status
    UploadedFile.query.filter_by(task_id=task_id).update({
        'status': 'Completed',
        'detection_status': detection
    })
    db.session.commit()

    return jsonify({"task_id": task_id, "detection": detection, "status": status}), 200


@callback_bp.route('/get_report/<task_id>', methods=['GET'])
def get_report(task_id):
    # URL of the Cuckoo API to retrieve the report
    cuckoo_report_url = f"http://localhost:8000/apiv2/tasks/get/report/{task_id}/"

    try:
        # Send a GET request to retrieve the report from the Cuckoo API
        response = requests.get(cuckoo_report_url)
        
        # Check if the request was successful
        if response.status_code == 200:
            report_data = response.json()  # Convert the report to JSON format
            return jsonify(report_data), 200
        else:
            return jsonify({"error": f"Failed to retrieve report for task_id {task_id}: {response.status_code}"}), 500

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Request to Cuckoo API failed: {str(e)}"}), 500