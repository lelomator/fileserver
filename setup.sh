#!/bin/bash

# Beende das Skript bei einem Fehler
set -e

# Wechsle in das Server-Verzeichnis
cd /mnt/server

# Erstelle eine virtuelle Umgebung
echo "Creating virtual environment..."
python3 -m venv venv

# Aktiviere die virtuelle Umgebung
source venv/bin/activate

# Installiere zusätzliche Python-Pakete, falls angegeben
if [[ ! -z "${PY_PACKAGES}" ]]; then
    echo "Installing additional Python packages: ${PY_PACKAGES}"
    pip install -U ${PY_PACKAGES}
fi

# Überprüfe, ob die requirements.txt-Datei existiert, und installiere die Abhängigkeiten
if [[ -f /mnt/server/${REQUIREMENTS_FILE} ]]; then
    echo "Installing Python dependencies from ${REQUIREMENTS_FILE}..."
    pip install -U -r ${REQUIREMENTS_FILE}
else
    echo "No ${REQUIREMENTS_FILE} found, skipping dependency installation."
fi

# Erstelle das Verzeichnis für hochgeladene Dateien, falls es nicht existiert
mkdir -p user-files

echo "Setup complete. The environment is ready to start the Flask application."

