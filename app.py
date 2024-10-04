# app.py

from app import create_app, db
from app.models import User, UploadedFile

app = create_app()

# Tạo cơ sở dữ liệu nếu chưa tồn tại
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)