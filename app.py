import os
from flask import Flask, request, redirect, url_for, session, jsonify, send_from_directory, flash
from flask_oauthlib.client import OAuth
import requests

# Flask setup
app = Flask(__name__)
app.secret_key = 'YOUR_SECRET_KEY'
app.config['UPLOAD_FOLDER'] = 'user-files/'

# Ensure the upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# VirusTotal API key
VIRUSTOTAL_API_KEY = 'YOUR_VIRUSTOTAL_API_KEY'

# OAuth setup
oauth = OAuth(app)
google = oauth.remote_app(
    'google',
    consumer_key='YOUR_GOOGLE_CLIENT_ID',
    consumer_secret='YOUR_GOOGLE_CLIENT_SECRET',
    request_token_params={
        'scope': 'email',
    },
    base_url='https://www.googleapis.com/oauth2/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
)

# Product key validation (simplified version)
VALID_PRODUCT_KEY = "VALID_KEY"
product_key_valid = False

@app.route('/')
def index():
    if not product_key_valid:
        return redirect(url_for('product_key'))
    return 'Welcome to the file hosting server. <a href="/login">Login with Google</a>'

@app.route('/product-key', methods=['GET', 'POST'])
def product_key():
    global product_key_valid
    if request.method == 'POST':
        key = request.form.get('product_key')
        if key == VALID_PRODUCT_KEY:
            product_key_valid = True
            return redirect(url_for('login'))
        else:
            return 'Invalid Product Key. Try again.'
    return '''
    <form method="post">
        Product Key: <input type="text" name="product_key">
        <input type="submit" value="Submit">
    </form>
    '''

@app.route('/login')
def login():
    return google.authorize(callback=url_for('authorized', _external=True))

@app.route('/logout')
def logout():
    session.pop('google_token')
    return redirect(url_for('index'))

@app.route('/login/authorized')
def authorized():
    response = google.authorized_response()
    if response is None or response.get('access_token') is None:
        return 'Access denied: reason={} error={}'.format(
            request.args['error_reason'],
            request.args['error_description']
        )
    session['google_token'] = (response['access_token'], '')
    return redirect(url_for('files'))

@google.tokengetter
def get_google_oauth_token():
    return session.get('google_token')

# Route to list uploaded files
@app.route('/files', methods=['GET'])
def files():
    if 'google_token' not in session:
        return redirect(url_for('login'))
    
    files_list = os.listdir(app.config['UPLOAD_FOLDER'])
    return jsonify(files_list)

# Route to handle file uploads
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'google_token' not in session:
        return redirect(url_for('login'))

    if 'file' not in request.files:
        return 'No file part'
    
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'

    # Save the file temporarily
    temp_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(temp_path)

    # Scan the file with VirusTotal
    is_safe = scan_with_virustotal(temp_path)
    if not is_safe:
        os.remove(temp_path)
        return 'File contains a virus and has been rejected.'

    return 'File uploaded and scanned successfully'

# Route to download a file
@app.route('/files/<filename>')
def download_file(filename):
    if 'google_token' not in session:
        return redirect(url_for('login'))

    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Function to scan file with VirusTotal
def scan_with_virustotal(file_path):
    url = 'https://www.virustotal.com/vtapi/v2/file/scan'
    files = {'file': open(file_path, 'rb')}
    params = {'apikey': VIRUSTOTAL_API_KEY}
    
    response = requests.post(url, files=files, params=params)
    result = response.json()

    scan_id = result['scan_id']

    # Retrieve the scan results
    report_url = 'https://www.virustotal.com/vtapi/v2/file/report'
    report_params = {'apikey': VIRUSTOTAL_API_KEY, 'resource': scan_id}
    
    report_response = requests.get(report_url, params=report_params)
    report_result = report_response.json()

    # Check if the file is clean
    return report_result['positives'] == 0

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
