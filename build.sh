#!/usr/bin/env bash
# Exit on error
set -o errexit

# Installer les dépendances
pip install -r requirements.txt

# Collecter les fichiers statiques
python manage.py collectstatic --no-input

# Appliquer les migrations de base de données
python manage.py migrate 