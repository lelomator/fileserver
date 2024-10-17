import os
import hashlib
from flask import Flask, request, redirect, url_for, session, send_from_directory, render_template

# Flask setup
app = Flask(__name__)
app.secret_key = 'YOUR_SECRET_KEY'
app.config['UPLOAD_FOLDER'] = 'user-files/'
app.config['PASSWORD_FILE'] = 'passwords.txt'  # Datei zur Speicherung der gehashten Passwörter
app.config['PORT'] = 25503  # Port für den Flask-Server

# Ensure the upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Product key validation (simplified version)
VALID_PRODUCT_KEY = "123"
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

# Funktion zum Überprüfen, ob ein Passwort gesetzt wurde
def is_password_set():
    return os.path.exists(app.config['PASSWORD_FILE'])

@app.route('/')
def index():
    if not product_key_valid:
        return redirect(url_for('product_key'))
    if not is_password_set():
        return redirect(url_for('set_password'))
    return redirect(url_for('files_ui'))

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
            return render_template('product_key.html', error="Invalid Product Key. Try again.")
    return render_template('product_key.html')

# Passwort setzen (nur einmal)
@app.route('/set-password', methods=['GET', 'POST'])
def set_password():
    if not product_key_valid:
        return redirect(url_for('product_key'))

    if is_password_set():
        return 'Password has already been set. Please <a href="/login">login</a>.'

    if request.method == 'POST':
        password = request.form.get('password')
        if password:
            hashed = hash_password(password)
            save_password(hashed)
            return 'Password set successfully. You can now <a href="/login">login</a>.'
        else:
            return render_template('set_password.html', error="Password cannot be empty.")
    
    return render_template('set_password.html')

# Login mit Passwort
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        if check_password(password):
            session['logged_in'] = True
            return redirect(url_for('files_ui'))
        else:
            return render_template('login.html', error="Incorrect password. Try again.")
    
    return render_template('login.html')

# Route zum Abmelden
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

# Benutzeroberfläche für Dateien anzeigen
@app.route('/files', methods=['GET'])
def files_ui():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    files_list = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('files.html', files=files_list)

# Route zum Hochladen von Dateien und Ordnern
@app.route('/upload', methods=['POST'])
def upload_file():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    # Verzeichnisse und mehrere Dateien hochladen
    if 'file' not in request.files:
        return 'No file part'
    
    files = request.files.getlist('file')
    
    for file in files:
        if file.filename == '':
            continue
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)

    return redirect(url_for('files_ui'))

# Route zum Herunterladen von Dateien
@app.route('/download/<filename>')
def download_file(filename):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Run the app with configurable port
if __name__ == '__main__':
    port = int(os.environ.get('PORT', app.config['PORT']))  # Port aus Umgebungsvariable oder Config
    app.run(debug=True, host='0.0.0.0', port=port)
