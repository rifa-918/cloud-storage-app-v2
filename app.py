from flask import Flask, render_template, request
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from flask_mail import Mail, Message
import os

app = Flask(__name__)

# Google Drive API Setup
SERVICE_ACCOUNT_FILE = "service_account.json"
FOLDER_ID = "1Rbewt_olwEAP1bfuWhp7XSCBmXxGacdP"
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=["https://www.googleapis.com/auth/drive"]
)
drive_service = build("drive", "v3", credentials=credentials)

# Flask-Mail Configuration
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = "khansadiya9901@gmail.com"  # Your Gmail
app.config["MAIL_PASSWORD"] = "bvhs yqjw hrzn opqz"  # Your App Password
app.config["MAIL_DEFAULT_SENDER"] = "khansadiya9901@gmail.com"

mail = Mail(app)

# Ensure 'uploads' folder exists
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def upload_file_to_drive(file_path, file_name):
    """Uploads a file to Google Drive."""
    file_metadata = {
        "name": file_name,
        "parents": [FOLDER_ID]
    }
    media = MediaFileUpload(file_path, resumable=True)
    uploaded_file = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id"
    ).execute()
    return uploaded_file.get("id")

def send_email_notification(user_email, file_name, file_id):
    """Sends an email to the user with the file upload details."""
    subject = "File Upload Successful!"
    file_link = f"https://drive.google.com/file/d/{file_id}/view"
    body = f"""
    Hello,<br><br>
    Your file '<b>{file_name}</b>' has been successfully uploaded.<br>
    You can access it here: <a href="{file_link}" target="_blank">Click here to view your file</a>.<br><br>
    Thank you!
    """
    
    msg = Message(subject, recipients=[user_email])
    msg.html = body  # Using HTML to format the hyperlink
    mail.send(msg)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files or 'email' not in request.form:
        return "File or email missing!"

    file = request.files['file']
    user_email = request.form['email']

    if file.filename == '':
        return "No selected file"

    # Save the file in the 'uploads' folder
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)
    
    # Upload file to Google Drive
    file_id = upload_file_to_drive(file_path, file.filename)
    
    # Delete the file after upload
    os.remove(file_path)

    # Send notification email
    send_email_notification(user_email, file.filename, file_id)

    return f"File uploaded successfully! An email has been sent to {user_email}."

if __name__ == '__main__':
    os.makedirs("uploads", exist_ok=True)
    app.run(debug=True)
