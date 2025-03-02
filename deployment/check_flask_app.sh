#!/bin/bash
# Script to check Flask application structure

echo "Checking Flask application structure..."
find /app -type f -name '*.py' | sort

echo -e "\nChecking for Flask application entry point..."
grep -r 'app = Flask' /app

echo -e "\nChecking for routes..."
grep -r '@app.route' /app

echo -e "\nChecking for WSGI entry point..."
grep -r 'if __name__ == "__main__"' /app

echo -e "\nChecking for Gunicorn configuration..."
find /app -name 'gunicorn.conf.py' || echo "No Gunicorn configuration file found"

echo -e "\nChecking environment variables..."
env | grep -v PASSWORD | grep -v SECRET | grep -v KEY

echo -e "\nChecking installed Python packages..."
pip list 