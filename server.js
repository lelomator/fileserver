const express = require('express');
const multer = require('multer');
const fs = require('fs');
const path = require('path');
const cookieParser = require('cookie-parser');

const app = express();
const uploadDir = path.join(__dirname, 'uploads');
const correctPassword = 'meinpasswort'; // Setze hier das gewünschte Passwort

// Multer Speicher für hochgeladene Dateien
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    if (!fs.existsSync(uploadDir)) {
      fs.mkdirSync(uploadDir, { recursive: true });
    }
    cb(null, uploadDir);
  },
  filename: (req, file, cb) => {
    const sanitizedFilename = file.originalname.replace(/\s+/g, '_');
    cb(null, Date.now() + '-' + sanitizedFilename);
  },
});

const upload = multer({ storage });

// Middleware, um statische Dateien aus dem "uploads"-Ordner zu servieren
app.use('/uploads', express.static(uploadDir));
app.use(cookieParser());
app.use(express.urlencoded({ extended: true }));

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
  res.send(`
    <form method="POST" action="/login">
      <label>Passwort: <input type="password" name="password"></label>
      <button type="submit">Login</button>
    </form>
  `);
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

// Ab hier geschützte Routen, nur zugänglich, wenn das Passwort korrekt ist
app.use(checkPassword);

// HTML Seite anzeigen (geschützt)
app.get('/', (req, res) => {
  res.sendFile(__dirname + '/index.html');
});

// Datei Upload Route (geschützt)
app.post('/upload', upload.array('files'), (req, res) => {
  if (!req.files || req.files.length === 0) {
    return res.status(400).json({ error: 'No files uploaded' });
  }
  res.redirect('/');
});

// Liste der hochgeladenen Dateien anzeigen (geschützt)
app.get('/files', (req, res) => {
  fs.readdir(uploadDir, (err, files) => {
    if (err) {
      return res.status(500).json({ error: 'Could not list the files' });
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
    res.status(404).json({ error: 'File not found' });
  }
});

// Route zum Löschen von Dateien (geschützt)
app.delete('/delete/:filename', (req, res) => {
  const filename = req.params.filename;
  const filePath = path.join(uploadDir, filename);
  if (fs.existsSync(filePath)) {
    fs.unlink(filePath, (err) => {
      if (err) {
        return res.status(500).json({ error: 'Could not delete the file' });
      }
      res.json({ success: true });
    });
  } else {
    res.status(404).json({ error: 'File not found' });
  }
});

app.listen(25503, () => {
  console.log('Server running on http://localhost:3000');
});
