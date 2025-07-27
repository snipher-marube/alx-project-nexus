#!/bin/bash

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Run Django management commands
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput --clear

# Install drf-yasg static files specifically
python -c "import os; from drf_yasg import openapi; print('Drf-yasg static files location:', os.path.dirname(openapi.__file__))"