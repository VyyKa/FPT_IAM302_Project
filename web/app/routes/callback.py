from flask import Blueprint, request, jsonify, current_app, session
from app.models import UploadedFile
from app import db
from app.utils.response_utils import response_dict
from werkzeug.utils import secure_filename
import os
import uuid
import requests
import threading

callback_bp = Blueprint('callback_bp', __name__)



@callback_bp.route('/callback', methods=['POST'])
def callback():
    # Get JSON data from the request body
    data = request.get_json()
    if not data or 'task_id' not in data:
        return jsonify({"error": "task_id is required"}), 400
    
    task_id = data.get('task_id', None)
    detection = data.get('detection', 'Unknown')
    status = data.get('status', 'Unknown')

    if task_id is None:
        return jsonify({"error": "task_id is required"}), 400

    if status != "success":
        UploadedFile.query.filter_by(task_id=task_id).update({'status': 'Failed'})
        db.session.commit()

    # Xu ly neu success
    
    # Update detection to the database UploadedFile
    UploadedFile.query.filter_by(task_id=task_id).update({'detection_status': detection})
    db.session.commit()

    return jsonify({"task_id": task_id, "detection": detection, "status": status}), 200


@callback_bp.route('/get_report/<:id>', methods=['GET'])
def get_report(id):
    pass
    # Create a requests to get the report from the Cuckoo API