import os
import hashlib
from flask import Flask, request, redirect, url_for, session, jsonify, send_from_directory, flash

# Flask setup
app = Flask(__name__)
app.secret_key = 'YOUR_SECRET_KEY'
app.config['UPLOAD_FOLDER'] = 'user-files/'
app.config['PASSWORD_FILE'] = 'passwords.txt'  # Datei zur Speicherung der gehashten Passwörter

# Ensure the upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Product key validation (simplified version)
VALID_PRODUCT_KEY = "VALID_KEY"
product_key_valid = False

# Hilfsfunktion zum Hashen eines Passworts
def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

# Funktion zum Speichern des gehashten Passworts
def save_password(hash):
    with open(app.config['PASSWORD_FILE'], 'w') as f:
        f.write(hash)

# Funktion zum Überprüfen des Passworts
def check_password(password):
    if not os.path.exists(app.config['PASSWORD_FILE']):
        return False
    with open(app.config['PASSWORD_FILE'], 'r') as f:
        saved_hash = f.read().strip()
    return hash_password(password) == saved_hash

@app.route('/')
def index():
    if not product_key_valid:
        return redirect(url_for('product_key'))
    return 'Welcome to the file hosting server. <a href="/set-password">Set a password</a> if not already set, or <a href="/login">Login</a>.'

# Produkt-Key-Eingabe
@app.route('/product-key', methods=['GET', 'POST'])
def product_key():
    global product_key_valid
    if request.method == 'POST':
        key = request.form.get('product_key')
        if key == VALID_PRODUCT_KEY:
            product_key_valid = True
            return redirect(url_for('set_password'))
        else:
            return 'Invalid Product Key. Try again.'
    return '''
    <form method="post">
        Product Key: <input type="text" name="product_key">
        <input type="submit" value="Submit">
    </form>
    '''

# Passwort setzen
@app.route('/set-password', methods=['GET', 'POST'])
def set_password():
    if not product_key_valid:
        return redirect(url_for('product_key'))
    
    if request.method == 'POST':
        password = request.form.get('password')
        if password:
            hashed = hash_password(password)
            save_password(hashed)
            return 'Password set successfully. You can now <a href="/login">login</a>.'
        else:
            return 'Password cannot be empty.'
    
    return '''
    <form method="post">
        Set a Password: <input type="password" name="password">
        <input type="submit" value="Set Password">
    </form>
    '''

# Login mit Passwort
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        if check_password(password):
            session['logged_in'] = True
            return redirect(url_for('files'))
        else:
            return 'Incorrect password. Try again.'
    
    return '''
    <form method="post">
        Enter Password: <input type="password" name="password">
        <input type="submit" value="Login">
    </form>
    '''

# Route zum Abmelden
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

# Route zum Anzeigen der Dateien
@app.route('/files', methods=['GET'])
def files():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    files_list = os.listdir(app.config['UPLOAD_FOLDER'])
    return jsonify(files_list)

# Route zum Hochladen von Dateien
@app.route('/upload', methods=['POST'])
def upload_file():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if 'file' not in request.files:
        return 'No file part'
    
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'

    # Save the file temporarily
    temp_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(temp_path)

    # Du kannst hier auch eine Funktion zum Scannen der Datei hinzufügen (z.B. mit VirusTotal)
    return 'File uploaded successfully'

# Route zum Herunterladen von Dateien
@app.route('/files/<filename>')
def download_file(filename):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
