## Manual Installation

For development without Docker:

1. **Clone the repository**
   ```bash
   git clone https://github.com/snipher-marube/alx-project-nexus.git
   cd alx-project-nexus
   ```

2. **Create and activate virtual environment**
   ```bash
   # Using venv
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # venv\Scripts\activate  # Windows

   # Or using conda
   conda create -n nexus python=3.9
   conda activate nexus
   ```

3. **Install dependencies**
   ```bash
   # Production dependencies
   pip install -r requirements.txt

   # Development dependencies
   pip install -r requirements-dev.txt
   ```

4. **Environment setup**
   ```bash
   # Copy environment template
   cp .env.example .env

   # Edit the .env file with your configuration
   nano .env
   ```

## Environment Configuration

Create a `.env` file with the following configuration:

```env
# =============================================================================
# DJANGO SETTINGS
# =============================================================================
SECRET_KEY=your_super_secure_secret_key_here_min_50_chars_recommended
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
DJANGO_SETTINGS_MODULE=ecommerce.settings.development

# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================
DATABASE_URL=postgres://nexus_user:secure_password@localhost:5432/nexus_db
DB_NAME=nexus_db
DB_USER=nexus_user
DB_PASSWORD=secure_password
DB_HOST=localhost
DB_PORT=5432

# =============================================================================
# REDIS CONFIGURATION
# =============================================================================
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2

# =============================================================================
# EMAIL CONFIGURATION
# =============================================================================
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_specific_password

# =============================================================================
# PAYMENT GATEWAYS
# =============================================================================
STRIPE_PUBLIC_KEY=pk_test_your_stripe_public_key
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
PAYPAL_CLIENT_ID=your_paypal_client_id
PAYPAL_CLIENT_SECRET=your_paypal_client_secret

# =============================================================================
# THIRD-PARTY SERVICES
# =============================================================================
SENTRY_DSN=https://your_sentry_dsn@sentry.io/project_id
ELASTICSEARCH_URL=http://localhost:9200
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_STORAGE_BUCKET_NAME=your_s3_bucket_name

# =============================================================================
# DEVELOPMENT SETTINGS
# =============================================================================
DJANGO_LOG_LEVEL=INFO
SQL_DEBUG=False
ENABLE_SILK_PROFILING=True
```

5. **Database setup**
   ```bash
   # static files collection
    python manage.py collectstatic --noinput

   # Create database migrations
   python manage.py makemigrations

   # Apply migrations
   python manage.py migrate

   # Load initial data (optional)
   python manage.py loaddata fixtures/initial_data.json
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Start development server**
   ```bash
   # Start Django development server
   python manage.py runserver

   # Start Celery worker (in another terminal)
   celery -A ecommerce worker -l info

   # Start Celery beat scheduler (in another terminal)
   celery -A ecommerce beat -l info
   ```
