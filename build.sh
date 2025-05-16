#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

# Create symbolic link for app.py to fix deployment
echo "from gestion_vehicules.wsgi import application as app" > app.py

cd test11
git add .
