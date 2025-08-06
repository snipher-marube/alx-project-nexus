# Project Structure

This document provides an overview of the project's directory structure.

```
.
├── .github/
│   ├── ISSUE_TEMPLATE/
│   └── workflows/
├── ecommerce/
│   ├── settings/
│   ├── __init__.py
│   ├── asgi.py
│   ├── urls.py
│   └── wsgi.py
├── frontend/
│   └── my-app/
├── orders/
│   ├── migrations/
│   └── ...
├── payments/
│   ├── migrations/
│   └── ...
├── products/
│   ├── migrations/
│   └── ...
├── staticfiles/
│   └── ...
├── templates/
│   └── ...
├── users/
│   ├── migrations/
│   └── ...
├── wiki/
│   └── ...
├── .env.test
├── .gitignore
├── .hintrc
├── manage.py
├── pytest.ini
├── README.md
├── requirements.txt
└── setup.sh
```

## Directory Descriptions

-   **`.github/`**: Contains GitHub-specific files, such as issue templates and workflow configurations.
-   **`ecommerce/`**: The main Django project directory.
    -   **`settings/`**: Contains the project's settings files, separated by environment (base, development, production).
    -   **`urls.py`**: The main URL configuration for the project.
-   **`frontend/`**: Contains the frontend application.
-   **`orders/`**: The Django app for managing orders.
-   **`payments/`**: The Django app for managing payments.
-   **`products/`**: The Django app for managing products.
-   **`staticfiles/`**: The directory where static files are collected for deployment.
-   **`templates/`**: Contains the Django templates for the project.
-   **`users/`**: The Django app for managing users and authentication.
-   **`wiki/`**: Contains the project's documentation.
-   **`.env.test`**: The environment variables file for the test environment.
-   **`manage.py`**: The Django management script.
-   **`pytest.ini`**: The configuration file for pytest.
-   **`README.md`**: The main README file for the project.
-   **`requirements.txt`**: The list of Python dependencies for the project.
-   **`setup.sh`**: A script for setting up the project.
