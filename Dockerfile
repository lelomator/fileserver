# Verwende ein Python-Image als Basis
FROM python:3.8-slim

# Setze das Arbeitsverzeichnis im Container
WORKDIR /app

# Kopiere alle Dateien in das Arbeitsverzeichnis
COPY . /app

# Installiere die Python-Abhängigkeiten
RUN python3 -m venv venv && \
    . venv/bin/activate && \
    pip install -r requirements.txt

# Erstelle den Upload-Ordner, falls er nicht existiert
RUN mkdir -p user-files

# Exponiere den Flask-Port (Pterodactyl wird den internen Port an einen externen weiterleiten)
EXPOSE 5000

# Startbefehl für den Flask-Server
CMD ["/app/venv/bin/python", "app.py"]
