from flask import Blueprint, request, jsonify, current_app, session
from app.models import UploadedFile
from app import db
from app.utils.response_utils import response_dict
from werkzeug.utils import secure_filename
import os
import uuid

upload_bp = Blueprint('upload_bp', __name__)

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
        
        # Retrieve user_id from the session if the user is logged in
        user_id = session.get('user_id')  # None if not logged in
        
        uploaded_files = []        
        for file in files:
            filename = secure_filename(file.filename)  # Secure the file name
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)

            # Check if the file already exists in the directory
            if os.path.exists(filepath):
                # Create a new file name with UUID to avoid duplication
                unique_filename = f"{uuid.uuid4().hex}_{filename}"
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
                print(f"File {filename} already exists, saving as: {unique_filename}")
            else:
                unique_filename = filename

            # Save the file to the specified path
            try:
                file.save(filepath)
            except Exception as e:
                print(f"Error saving file {filename}: {e}")
                return jsonify(response_dict('error', f"Failed to save file {filename}", {})), 500

            # Create a new record for the file in the database
            new_file = UploadedFile(filename=unique_filename, filepath=filepath, user_id=user_id)
            db.session.add(new_file)
            db.session.commit()

            # Simulate the file analysis status
            new_file.status = "In Progress"
            db.session.commit()

            # Example: File analysis completed successfully
            # new_file.status = "Analyzed"  # Could be "Failed" if the analysis fails
            # db.session.commit()

            uploaded_files.append({
                'filename': new_file.filename,
                'status': new_file.status,
                'timestamp': new_file.timestamp
            })

        return jsonify(response_dict('success', 'File uploaded successfully!', {'files': uploaded_files})), 201

    except Exception as e:
        # Print detailed error for debugging
        print(f"Error during file upload: {e}")
        return jsonify(response_dict('error', 'Internal Server Error', {})), 500