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
    // Dateinamen anpassen: Leerzeichen durch Unterstriche ersetzen
    const sanitizedFilename = file.originalname.replace(/\s+/g, '_');
    cb(null, Date.now() + '-' + sanitizedFilename);
  },
});

const upload = multer({ storage });

// Middleware, um statische Dateien aus dem "uploads"-Ordner zu servieren
app.use('/uploads', express.static(uploadDir));

// HTML Seite anzeigen
app.get('/', (req, res) => {
  res.sendFile(__dirname + '/index.html');
});

// Datei Upload Route
app.post('/upload', upload.array('files'), (req, res) => {
  if (!req.files || req.files.length === 0) {
    return res.status(400).json({ error: 'No files uploaded' });
  }
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

// Herunterladen von Dateien ermöglichen
app.get('/download/:filename', (req, res) => {
  const filename = req.params.filename;
  const filePath = path.join(uploadDir, filename);
  if (fs.existsSync(filePath)) {
    res.download(filePath); // Datei wird zum Download angeboten
  } else {
    res.status(404).json({ error: 'File not found' });
  }
});

app.listen(3000, () => {
  console.log('Server running on http://localhost:3000');
});
