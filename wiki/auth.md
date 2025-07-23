
# Authentication API Documentation

## Table of Contents
1. [Overview](#overview)
2. [API Endpoints](#api-endpoints)
3. [Request/Response Examples](#requestresponse-examples)
4. [Error Handling](#error-handling)
5. [Security Considerations](#security-considerations)
6. [Rate Limiting](#rate-limiting)
7. [Token System](#token-system)

## Overview
This API provides user authentication services including:
- User registration with email verification
- Email verification flow
- User login/logout
- Profile management
- Account security features

## API Endpoints

### 1. User Registration
**Endpoint**: `POST /api/v1/auth/register/`

**Request Body**:
```json
{
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+254712345678",
  "user_type": "CUSTOMER",
  "password": "securePassword123!",
  "password2": "securePassword123!"
}
```

**Response**:
- Success (201 Created):
```json
{
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "is_verified": false
  },
  "message": "User created successfully. Please verify your email."
}
```

### 2. Email Verification
**Endpoint**: `GET /api/v1/auth/verify-email/<uuid:user_id>/<str:token>/`

**Response**:
- Success (200 OK):
```json
{
  "detail": "Email successfully verified",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "is_verified": true
  }
}
```

### 3. Resend Verification Email
**Endpoint**: `POST /api/v1/auth/resend-verification-email/`

**Headers**:
- `Authorization: Token <token>` (for authenticated users)

**Response**:
- Success (200 OK):
```json
{
  "detail": "Verification email sent successfully"
}
```

### 4. User Login
**Endpoint**: `POST /api/v1/auth/login/`

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "securePassword123!"
}
```

**Response**:
- Success (200 OK):
```json
{
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "first_name": "John",
    "is_verified": true
  },
  "token": "knox-auth-token",
  "message": "Login successful"
}
```

### 5. User Logout
**Endpoint**: `POST /api/v1/auth/logout/`

**Headers**:
- `Authorization: Token <token>`

**Response**:
- Success (200 OK):
```json
{
  "message": "Successfully logged out"
}
```

### 6. Get User Profile
**Endpoint**: `GET /api/v1/auth/me/`

**Headers**:
- `Authorization: Token <token>`

**Response**:
- Success (200 OK):
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "first_name": "John",
  "profile": {
    "gender": "M",
    "date_of_birth": "1990-01-01",
    "bio": "About me...",
    "age": 33
  }
}
```

## Request/Response Examples

### Complete Registration Flow
1. **Register**:
```bash
curl -X POST \
  http://localhost:8000/api/v1/auth/register/ \
  -H 'Content-Type: application/json' \
  -d '{
    "email": "new@example.com",
    "first_name": "Alice",
    "last_name": "Smith",
    "phone": "+254712345679",
    "user_type": "CUSTOMER",
    "password": "alice123!",
    "password2": "alice123!"
  }'
```

2. **Verify Email** (click link in email or):
```bash
curl -X GET \
  http://localhost:8000/api/v1/auth/verify-email/<user_id>/<token>/
```

3. **Login**:
```bash
curl -X POST \
  http://localhost:8000/api/v1/auth/login/ \
  -H 'Content-Type: application/json' \
  -d '{
    "email": "new@example.com",
    "password": "alice123!"
  }'
```

## Error Handling

### Common Errors
1. **Registration Errors**:
   - Email exists (400):
   ```json
   {"email": ["This email is already registered."]}
   ```
   - Password mismatch (400):
   ```json
   {"password": ["Password fields didn't match."]}
   ```

2. **Login Errors**:
   - Invalid credentials (401):
   ```json
   {"detail": "Unable to log in with provided credentials."}
   ```
   - Unverified account (401):
   ```json
   {"detail": "User account is not verified."}
   ```

3. **Verification Errors**:
   - Invalid token (400):
   ```json
   {"detail": "Invalid or expired verification token"}
   ```
   - Already verified (400):
   ```json
   {"detail": "Email is already verified"}
   ```

## Security Considerations
1. All endpoints use HTTPS
2. Passwords:
   - Never returned in responses
   - Stored hashed using Django's PBKDF2
3. Email verification:
   - Tokens expire after 24 hours
   - One-time use
4. Session management:
   - Knox tokens for authentication
   - Token destroyed on logout

## Rate Limiting
- Resend verification email: 5 requests/hour (per IP)
- Login attempts: Django's built-in rate limiting

## Token System
1. **Email Verification Tokens**:
   - Generated using `EmailVerificationTokenGenerator`
   - Contains:
     - User PK
     - Verification status
     - Timestamp
   - Valid for 24 hours

2. **Authentication Tokens**:
   - Knox tokens issued on login
   - Provide access to protected endpoints
   - Can be revoked individually or all at once

## Middleware Protection
The `AccountVerificationMiddleware` ensures:
- Unverified users can only access:
  - Registration
  - Login
  - Verification endpoints
- All other endpoints return 403 Forbidden for unverified users
