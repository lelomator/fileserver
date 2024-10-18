const express = require('express');
const multer = require('multer');
const fs = require('fs');
const path = require('path');

const app = express();
const uploadDir = path.join(__dirname, 'uploads');

// Multer Speicher für hochgeladene Dateien
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    if (!fs.existsSync(uploadDir)) {
      fs.mkdirSync(uploadDir, { recursive: true });
    }
    cb(null, uploadDir);
  },
  filename: (req, file, cb) => {
    cb(null, Date.now() + '-' + file.originalname);
  },
});

const upload = multer({ storage });

// Middleware, um statische Dateien aus dem "uploads" Ordner zu servieren
app.use('/uploads', express.static(uploadDir));

// HTML Seite anzeigen
app.get('/', (req, res) => {
  res.sendFile(__dirname + '/index.html');
});

// Datei Upload Route
app.post('/upload', upload.array('files'), (req, res) => {
  res.redirect('/');
});

// Liste der hochgeladenen Dateien anzeigen
app.get('/files', (req, res) => {
  fs.readdir(uploadDir, (err, files) => {
    if (err) {
      return res.status(500).json({ error: 'Could not list the files' });
    }
    res.json(files);
  });
});

app.listen(25503, () => {
  console.log('Server running on http://localhost:3000');
});
