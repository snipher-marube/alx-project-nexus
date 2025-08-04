## 🚀 Deployment

### 🌐 Production Deployment

#### Using Docker (Recommended)

```bash
# 1. Clone production branch
git clone -b production https://github.com/snipher-marube/alx-project-nexus.git
cd alx-project-nexus

# 2. Set up production environment
cp .env.example .env.production
# Edit .env.production with production values

# 3. Build and deploy
docker-compose -f docker-compose.prod.yml up --build -d

# 4. Run initial setup
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
```

#### AWS ECS Deployment

```bash
# 1. Build and push to ECR
aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-west-2.amazonaws.com
docker build -f docker/Dockerfile.prod -t nexus-api .
docker tag nexus-api:latest <account-id>.dkr.ecr.us-west-2.amazonaws.com/nexus-api:latest
docker push <account-id>.dkr.ecr.us-west-2.amazonaws.com/nexus-api:latest

# 2. Deploy to ECS
aws ecs update-service --cluster nexus-cluster --service nexus-api-service --force-new-deployment
```

### 🔧 Production Environment Variables

```env
# Essential production settings
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
DJANGO_SETTINGS_MODULE=ecommerce.settings.production

# Security settings
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# Database (Production)
DATABASE_URL=postgres://user:password@prod-db-host:5432/nexus_prod

# Cache (Production)
REDIS_URL=redis://prod-redis-host:6379/0

# Storage (AWS S3)
AWS_ACCESS_KEY_ID=your_production_access_key
AWS_SECRET_ACCESS_KEY=your_production_secret_key
AWS_STORAGE_BUCKET_NAME=nexus-production-assets
AWS_S3_REGION_NAME=us-west-2

# Monitoring
SENTRY_DSN=https://your-production-sentry-dsn@sentry.io/project
```

### 🔄 CI/CD Pipeline

The project uses **GitHub Actions** for automated testing and deployment:

```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Deploy to production
        run: |
          # Deployment commands
```
