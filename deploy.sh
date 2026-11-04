#!/bin/bash
# This shell script deploys a new version to PythonAnywhere.

PROJ_DIR=JAYDES
VENV=jaydes
PA_DOMAIN="samthropic.pythonanywhere.com"
PA_USER='samthropic'
echo "Project dir = $PROJ_DIR"
echo "PA domain = $PA_DOMAIN"
echo "Virtual env = $VENV"

if [ -z "$PA_PWD" ]
then
    echo "The PythonAnywhere password var (PA_PWD) must be set in the env."
    exit 1
fi

echo "PA user = $PA_USER"

echo "SSHing to PythonAnywhere."
sshpass -p "$PA_PWD" ssh -o "StrictHostKeyChecking no" $PA_USER@ssh.pythonanywhere.com << EOF
    cd ~/$PROJ_DIR; PA_USER=$PA_USER PROJ_DIR=~/$PROJ_DIR VENV=$VENV PA_DOMAIN=$PA_DOMAIN ./rebuild.sh
EOF
