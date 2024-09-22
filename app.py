# importing the required libraries
import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename # checks for vulnerability in the uploaded files and protects the server from dangerous files
from datetime import datetime
import bcrypt

# initialising the flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'longcyber'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///file_store.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define a model for users 
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

# Define a model for uploaded files
class UploadedFile(db.Model):
    __tablename__ = 'uploadedFile'
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100), nullable=False)
    filepath = db.Column(db.String(200), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
# Creating the upload folder
upload_folder = "uploads/"
if not os.path.exists(upload_folder):
    os.mkdir(upload_folder)
    
# Configuring the upload folder
app.config['UPLOAD_FOLDER'] = upload_folder

# Max size of the file (300MB)
app.config['MAX_CONTENT_LENGTH'] = 300 * 1024 * 1024 # 1 Mb 



# Configuring the allowed extensions
# allowed_extensions = ['docx', 'pdf']

# def check_file_extension(filename):
#     return filename.split('.')[-1] in allowed_extensions

# The path for uploading the file
@app.route('/')
def upload_file():
    return render_template('upload.html')

@app.route('/upload', methods = ['GET', 'POST'])
def uploadfile():
    if request.method == 'POST': # check if the method is post
        files = request.files.getlist('file') # get the file from the files object
        if not files:
            flash('No file uploaded', 'error')
            return redirect(url_for('upload_file'))
        
        for f in files:
            if f.filename == '':
                flash('No selected file', 'error') 
                return redirect(url_for('upload_file'))

            filename = secure_filename(f.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            f.save(filepath)
            
            # save file information (name and path) in the database
            new_file = UploadedFile(filename=filename, filepath=filepath)
            db.session.add(new_file)
            db.session.commit()
        
        flash('File(s) uploaded successfully', 'success')  # ensure this message is returned after all files are processed
        return redirect(url_for('upload_file'))

# route for login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Authentication logic goes here (check user credentials)
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            session['user_id'] = user.id
            flash('Login successful!', 'success')
            return redirect(url_for('upload_file'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

# Route for signup
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get['email']
        password = request.form.get('password')
        hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Check if the username or email already exists
        existing_user = User.query.filter((User.email == email) | (User.username == username)).first()
        if existing_user:
            flash('Username or email already exists', 'error')
            return redirect(url_for('signup'))
        
        # Create a new user
        new_user = User(username=username, email=email, password=hashed_pw)  # Add password hashing for security
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Signup successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'error')
        
    return render_template('signup.html')
    
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
    app.run(debug=True) # enable debug for better error messages during development