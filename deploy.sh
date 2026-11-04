#!/bin/bash
# Deploy to PythonAnywhere over the HTTP API (no SSH).
# Works on free accounts. Pulls are done by rebuild.sh on the server
# (run manually in a Bash console, or from a scheduled task).

set -e

PA_USER=samthropic
PA_DOMAIN=samthropic.pythonanywhere.com
PA_HOST=www.pythonanywhere.com

echo "PA user = $PA_USER"
echo "PA domain = $PA_DOMAIN"

if [ -z "$PA_API_TOKEN" ]
then
    echo "The PythonAnywhere API token var (PA_API_TOKEN) must be set in the env."
    echo "Create one at https://www.pythonanywhere.com/account/#api_token"
    exit 1
fi

RELOAD_URL="https://${PA_HOST}/api/v0/user/${PA_USER}/webapps/${PA_DOMAIN}/reload/"

echo "Reloading web app via PythonAnywhere API."
HTTP_CODE=$(curl -sS -o /tmp/pa_reload_body.txt -w "%{http_code}" \
    -X POST \
    -H "Authorization: Token ${PA_API_TOKEN}" \
    "$RELOAD_URL")

echo "Reload response ($HTTP_CODE):"
cat /tmp/pa_reload_body.txt
echo

if [ "$HTTP_CODE" != "200" ]
then
    echo "Reload failed."
    exit 1
fi

echo "Reload requested. On PythonAnywhere, keep code current with:"
echo "  cd ~/JAYDES && ./rebuild.sh"
echo "(or run that from a scheduled task). Free accounts cannot git-pull over SSH."
