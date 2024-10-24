from flask import Blueprint, request, jsonify, current_app, session
from app.models import UploadedFile
from app import db
from app.utils.response_utils import response_dict
from werkzeug.utils import secure_filename
import os
import uuid
import requests
import threading

upload_bp = Blueprint('upload_bp', __name__)

# Create a function threading to simulate file processing
def process_file(file_id):
    # Get the file from the database
    file = UploadedFile.query.get(file_id)
    if not file:
        print(f"File with ID {file_id} not found")
        return

    # Post this file to http://localhost:8000/apiv2/tasks/create/file
    url = current_app.config['CUCKOO_CREATE_FILE_URL']
    response = requests.post(url, files={'file': open(file.filepath, 'rb')})

    # Handle response and update the status of the file
    if response.status_code == 200:
        # Update the file status to "Processing"
        file.status = "Processing"
        db.session.commit()
    else:
        # Update the file status to "Failed"
        file.status = "Failed"
        db.session.commit()
        return

    url = current_app.config['ML_ADD_TASK_URL']
    response = requests.post(url, json=response.json())

    if response.status_code == 200:
        # Update the file status to "Processing"
        file.status = "Processing"
        db.session.commit()
    else:
        # Update the file status to "Failed"
        file.status = "Failed"
        db.session.commit()


@upload_bp.route('/upload', methods=['POST'])
def upload_files():
    try:
        # Check if the 'file' part exists in the request
        if 'file' not in request.files:
            return jsonify(response_dict('error', 'No file part in the request', {})), 400

        # Get the list of files from the request
        files = request.files.getlist('file')
        if not files or files[0].filename == '':
            return jsonify(response_dict('error', 'No file selected for uploading', {})), 400
        
        # Retrieve user_id from session
        user_id = session.get('user_id')  # None if not logged in
        
        if user_id is None:
            return jsonify(response_dict('error', 'User not authenticated', {})), 403
        
        uploaded_files = []        
        for file in files:
            filename = secure_filename(file.filename)  # Secure the file name
            absolute_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            relative_path = os.path.join('uploads', filename)  
            # filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)

            # Handle file name duplication
            if os.path.exists(absolute_path):
                # Create a new file name with UUID to avoid duplication
                unique_filename = f"{uuid.uuid4().hex}_{filename}"
                # filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
                absolute_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
                relative_path = os.path.join('uploads', unique_filename)
                print(f"File {filename} already exists, saving as: {unique_filename}")
            else:
                unique_filename = filename

            # Save the file
            try:
                file.save(absolute_path)
            except Exception as e:
                print(f"Error saving file {filename}: {e}")
                return jsonify(response_dict('error', f"Failed to save file {filename}", {})), 500

            # Create new record in the database
            new_file = UploadedFile(filename=unique_filename, filepath=relative_path, user_id=user_id)
            db.session.add(new_file)
            db.session.commit()

            # Save the initial file upload and set the status to "In Progress"
            new_file.status = "Uploaded"
            db.session.commit()

            # Simulate file processing or malware analysis
            # try:
            #     # Perform some analysis here...
            #     # Example: Assume analysis is successful and we detect no issues
            #     new_file.status = "Clean"
            #     db.session.commit()
            # except AnalysisError as e:
            #     # If something went wrong during analysis, mark it as failed
            #     new_file.status = "Failed"
            #     db.session.commit()

            # If file is found to be malicious:
            # new_file.status = "Malicious"
            # db.session.commit()
            
             # Prepare the uploaded file details for response
            uploaded_files.append({
                'filename': new_file.filename,
                'status': new_file.status,
                'timestamp': new_file.timestamp
            })

            # Start a new thread to process the file
            threading.Thread(target=process_file, args=(new_file.id,)).start()

        return jsonify(response_dict('success', 'File uploaded successfully!', {'files': uploaded_files})), 201

    except Exception as e:
        # Print detailed error for debugging
        print(f"Error during file upload: {e}")
        return jsonify(response_dict('error', 'Internal Server Error', {})), 500