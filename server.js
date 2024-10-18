const express = require('express');
const multer = require('multer');
const fs = require('fs');
const path = require('path');
const cookieParser = require('cookie-parser');

const app = express();
const uploadDir = path.join(__dirname, 'uploads');
const correctPassword = 'meinpasswort'; // Setze hier das gewünschte Passwort

// Middleware für statische Dateien (CSS usw.)
app.use(express.static(path.join(__dirname, 'public')));
app.use('/uploads', express.static(uploadDir)); // Bereitstellung von hochgeladenen Dateien
app.use(cookieParser());
app.use(express.urlencoded({ extended: true }));

// Multer-Konfiguration
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    const folderPath = path.join(uploadDir, path.dirname(file.originalname)); // Unterordnerstruktur beibehalten
    fs.mkdirSync(folderPath, { recursive: true });
    cb(null, folderPath); // Dateien im richtigen Verzeichnis speichern
  },
  filename: (req, file, cb) => {
    cb(null, path.basename(file.originalname)); // Nur der Dateiname ohne Pfad
  }
});

const upload = multer({
  storage,
  limits: {
    fileSize: 100 * 1024 * 1024, // Setze das Limit für jede Datei auf 100 MB
    files: 500 // Maximal 500 Dateien gleichzeitig
  }
});

// Funktion zur Passwortprüfung
function checkPassword(req, res, next) {
  const userPassword = req.cookies.password;
  if (userPassword === correctPassword) {
    return next();
  } else {
    return res.redirect('/login');
  }
}

// Route für die Login-Seite
app.get('/login', (req, res) => {
  res.sendFile(__dirname + '/login.html');
});

// POST-Route für das Login
app.post('/login', (req, res) => {
  const { password } = req.body;
  if (password === correctPassword) {
    res.cookie('password', password, { httpOnly: true });
    res.redirect('/');
  } else {
    res.send('Falsches Passwort. <a href="/login">Erneut versuchen</a>');
  }
});

// Geschützte Routen ab hier
app.use(checkPassword);

// HTML Seite anzeigen (geschützt)
app.get('/', (req, res) => {
  res.sendFile(__dirname + '/index.html');
});

// Datei Upload Route (geschützt)
app.post('/upload', upload.array('files'), (req, res) => {
  req.files.forEach(file => {
    console.log('Hochgeladen:', file.originalname); // Überprüfen der hochgeladenen Dateinamen
  });

  if (!req.files || req.files.length === 0) {
    return res.status(400).json({ error: 'Keine Dateien hochgeladen' });
  }
  res.redirect('/');
});

// Liste der hochgeladenen Dateien anzeigen (geschützt)
app.get('/files', (req, res) => {
  fs.readdir(uploadDir, (err, files) => {
    if (err) {
      return res.status(500).json({ error: 'Konnte die Dateien nicht auflisten' });
    }
    res.json(files);
  });
});

// Herunterladen von Dateien (geschützt)
app.get('/download/:filename', (req, res) => {
  const filename = req.params.filename;
  const filePath = path.join(uploadDir, filename);
  if (fs.existsSync(filePath)) {
    res.download(filePath);
  } else {
    res.status(404).json({ error: 'Datei nicht gefunden' });
  }
});

// Route zum Löschen von Dateien (geschützt)
app.delete('/delete/:filename', (req, res) => {
  const filename = req.params.filename;
  const filePath = path.join(uploadDir, filename);
  if (fs.existsSync(filePath)) {
    fs.unlink(filePath, (err) => {
      if (err) {
        return res.status(500).json({ error: 'Datei konnte nicht gelöscht werden' });
      }
      res.json({ success: true });
    });
  } else {
    res.status(404).json({ error: 'Datei nicht gefunden' });
  }
});

// Starte den Server
app.listen(25503, () => {
  console.log('Server läuft auf http://localhost:3000');
});
