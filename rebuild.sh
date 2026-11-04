#!/bin/bash
# Run this on PythonAnywhere (Bash console or scheduled task).
# Fetches new code, refreshes packages, and reloads the web app.

set -e

PA_USER=${PA_USER:-samthropic}
PA_DOMAIN=${PA_DOMAIN:-samthropic.pythonanywhere.com}
VENV=${VENV:-jaydes}
PROJ_DIR=${PROJ_DIR:-/home/$PA_USER/JAYDES}

cd "$PROJ_DIR"

echo "Pulling code from main"
git pull origin main

echo "Activate the virtual env $VENV"
# shellcheck source=/dev/null
source "/home/$PA_USER/.virtualenvs/$VENV/bin/activate"

echo "Install packages"
pip install --upgrade -r requirements.txt

echo "Reload web app $PA_DOMAIN"
if [ -n "$API_TOKEN" ]
then
    curl -sS -X POST \
        -H "Authorization: Token ${API_TOKEN}" \
        "https://www.pythonanywhere.com/api/v0/user/${PA_USER}/webapps/${PA_DOMAIN}/reload/"
    echo
else
    pa_reload_webapp.py "$PA_DOMAIN"
fi

echo "Finished rebuild."
