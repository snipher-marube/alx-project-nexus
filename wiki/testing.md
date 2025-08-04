## 🧪 Testing

ALX Project Nexus maintains **95%+ code coverage** with comprehensive testing strategies.

### 🏃‍♂️ Running Tests

```bash
# Run all tests
python manage.py test

# Run with coverage report
coverage run --source='.' manage.py test
coverage report -m
coverage html  # Generate HTML coverage report

# Run specific test modules
python manage.py test apps.products.tests
python manage.py test apps.authentication.tests.test_views

# Run tests with parallel execution
python manage.py test --parallel

# Run tests with specific settings
python manage.py test --settings=ecommerce.settings.testing

# Using pytest (recommended)
pytest
pytest --cov=apps --cov-report=html
pytest -v --tb=short
pytest -x  # Stop on first failure
```

### 🧪 Test Categories

#### Unit Tests
- **Model Tests**: Validate model behavior and constraints
- **Serializer Tests**: Test data serialization/deserialization
- **Utility Tests**: Test helper functions and utilities
- **Business Logic Tests**: Test core business rules

```bash
# Run only unit tests
pytest -m unit
```

#### Integration Tests
- **API Endpoint Tests**: Test complete request/response cycles
- **Database Integration**: Test database operations
- **External Service Integration**: Test third-party service interactions

```bash
# Run only integration tests
pytest -m integration
```

#### Performance Tests
- **Load Testing**: Test system under expected load
- **Stress Testing**: Test system limits
- **API Response Time**: Ensure acceptable response times

```bash
# Run performance tests
pytest -m performance
locust -f tests/performance/locustfile.py
```

### 📊 Test Coverage Report

Current test coverage by module:

| Module | Coverage | Lines | Missing |
|--------|----------|-------|---------|
| **authentication** | 98% | 245 | 5 |
| **products** | 97% | 312 | 9 |
| **orders** | 95% | 287 | 14 |
| **payments** | 94% | 198 | 12 |
| **core** | 99% | 156 | 2 |
| **Overall** | **96%** | **1,198** | **42** |

### 🔧 Testing Tools & Frameworks

- **pytest**: Primary testing framework
- **factory_boy**: Test data generation
- **freezegun**: Time mocking for tests
- **responses**: HTTP request mocking
- **django-test-utils**: Django-specific test utilities
