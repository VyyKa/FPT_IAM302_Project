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

def process_file(app, file_id):
    # Tạo ngữ cảnh ứng dụng cho thread
    with app.app_context():
        # Lấy file từ database
        file = UploadedFile.query.get(file_id)
        if not file:
            print(f"File with ID {file_id} not found")
            return

        # Đăng file lên endpoint được chỉ định
        url = app.config['CUCKOO_CREATE_FILE_URL']
        try:
            with open(file.filepath, 'rb') as f:
                response = requests.post(url, files={'file': f})

            # Cập nhật trạng thái file dựa trên kết quả phản hồi
            if response.status_code == 200:
                response_data = response.json()
                if response_data.get('error', True):
                    file.status = "Failed on upload"
                else:
                    task_ids = response_data.get('data', {}).get('task_ids', [])
                    if len(task_ids) > 0:
                        file.task_id = task_ids[0]
                        file.status = "Processing"
                    else:
                        file.status = "Failed to start processing"
            else:
                file.status = "Failed on upload"
            
            db.session.commit()
        except Exception as e:
            print(f"Error processing file {file.filename}: {e}")
            file.status = "Failed"
            db.session.commit()

@upload_bp.route('/upload', methods=['POST'])
def upload_files():
    try:
        # Kiểm tra xem phần 'file' có tồn tại trong request hay không
        if 'file' not in request.files:
            return jsonify(response_dict('error', 'No file part in the request', {})), 400

        files = request.files.getlist('file')
        if not files or files[0].filename == '':
            return jsonify(response_dict('error', 'No file selected for uploading', {})), 400
        
        user_id = session.get('user_id')
        if user_id is None:
            return jsonify(response_dict('error', 'User not authenticated', {})), 403

        uploaded_files = []
        for file in files:
            filename = secure_filename(file.filename)
            absolute_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            relative_path = os.path.join('uploads', filename)

            if os.path.exists(absolute_path):
                unique_filename = f"{uuid.uuid4().hex}_{filename}"
                absolute_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
                relative_path = os.path.join('uploads', unique_filename)
                print(f"File {filename} already exists, saving as: {unique_filename}")
            else:
                unique_filename = filename

            # Lưu file
            try:
                file.save(absolute_path)
            except Exception as e:
                print(f"Error saving file {filename}: {e}")
                return jsonify(response_dict('error', f"Failed to save file {filename}", {})), 500

            # Thêm record file vào database
            new_file = UploadedFile(filename=unique_filename, filepath=relative_path, user_id=user_id)
            db.session.add(new_file)
            db.session.commit()

            new_file.status = "Uploaded"
            db.session.commit()

            # Thêm thông tin file cho phản hồi
            uploaded_files.append({
                'filename': new_file.filename,
                'status': new_file.status,
                'timestamp': new_file.timestamp
            })

            # Khởi chạy một thread để xử lý file, truyền `current_app._get_current_object()` để dùng `app` trực tiếp
            threading.Thread(target=process_file, args=(current_app._get_current_object(), new_file.id)).start()

        return jsonify(response_dict('success', 'File uploaded successfully!', {'files': uploaded_files})), 201

    except Exception as e:
        print(f"Error during file upload: {e}")
        return jsonify(response_dict('error', 'Internal Server Error', {})), 500
