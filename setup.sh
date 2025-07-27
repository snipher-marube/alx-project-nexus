#!/bin/bash
<<<<<<< HEAD
# Clear pip cache
pip cache purge

# Install dependencies
pip install setuptools
pip install -r requirements.txt

# Run Django management commands
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput
=======
# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Run Django commands
python manage.py migrate
python manage.py collectstatic --noinput --clear
>>>>>>> 54dd383ec0051441f77a75a579fb238536be41b7
