# app.py

from app import create_app, db
from app.models import User, UploadedFile

app = create_app()

# Create the database if it doesn't exist
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)