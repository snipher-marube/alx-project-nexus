## 📚 API Documentation

ALX Project Nexus provides comprehensive API documentation with interactive testing capabilities.

### 📖 Documentation Access

| Documentation Type | URL | Description |
|-------------------|-----|-------------|
| **Swagger UI** | `{{baseURL}}/swagger/` | Interactive API testing interface |
| **Redoc** | `{{baseURL}}/redoc/` | Clean, responsive documentation |
| **OpenAPI Schema** | `{{baseURL}}/api/schema/` | Raw OpenAPI 3.0 specification |
| **Postman Collection** | `docs/postman/` | Ready-to-import Postman collection |

### 🔗 Core API Endpoints

#### Authentication Endpoints


##### User Registration
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

**Response** (201 Created):
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

##### Email Verification
**Endpoint**: `GET /api/v1/auth/verify-email/<uuid:user_id>/<str:token>/`

**Response** (200 OK):
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

##### Resend Verification Email
**Endpoint**: `POST /api/v1/auth/resend-verification-email/`

**Headers**:
- `Authorization: Token <token>` (for authenticated users)

**Response** (200 OK):
```json
{
  "detail": "Verification email sent successfully"
}
```

##### User Login
**Endpoint**: `POST /api/v1/auth/login/`

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "securePassword123!"
}
```

**Response** (200 OK):
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

##### User Logout
**Endpoint**: `POST /api/v1/auth/logout/`

**Headers**:
- `Authorization: Token <token>`

**Response** (200 OK):
```json
{
  "message": "Successfully logged out"
}
```

#### Product Management

##### Categories
| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/categories/` | GET | List all root categories | No |
| `/categories/` | POST | Create new category | Yes |
| `/categories/{slug}/` | GET | Get category details | No |
| `/categories/{slug}/children/` | GET | Get child categories | No |
| `/categories/{slug}/` | PUT/PATCH | Update category | Yes |
| `/categories/{slug}/` | DELETE | Delete category | Yes |

##### Brands
| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/brands/` | GET | List all brands | No |
| `/brands/` | POST | Create new brand | Yes |
| `/brands/{slug}/` | GET | Get brand details | No |
| `/brands/{slug}/` | PUT/PATCH | Update brand | Yes |
| `/brands/{slug}/` | DELETE | Delete brand | Yes |

##### Products
| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/products/` | GET | List all products | No |
| `/products/` | POST | Create new product | Yes |
| `/products/{slug}/` | GET | Get product details | No |
| `/products/{slug}/` | PUT/PATCH | Update product | Yes |
| `/products/{slug}/` | DELETE | Delete product | Yes |
| `/products/{slug}/add-image/` | POST | Add product image | Yes |
| `/products/{slug}/reviews/` | GET | List product reviews | No |
| `/products/{slug}/add-review/` | POST | Add product review | Yes (user) |

##### Product Variants
| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/product-variants/` | GET | List variants | Yes |
| `/product-variants/` | POST | Create variant | Yes |
| `/product-variants/{id}/` | GET | Get variant details | Yes |
| `/product-variants/{id}/` | PUT/PATCH | Update variant | Yes |
| `/product-variants/{id}/` | DELETE | Delete variant | Yes |

##### User Authentication
| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/api/v1/auth/register/` | POST | User registration | ❌ |
| `/api/v1/auth/login/` | POST | User login | ❌ |
| `/api/v1/auth/logout/` | POST | User logout | ✅ |
| `/api/v1/auth/refresh/` | POST | Refresh Knox token | ❌ |
| `/api/v1/auth/password/reset/` | POST | Password reset request | ❌ |
| `/api/v1/auth/password/confirm/` | POST | Confirm password reset | ❌ |

#### Product Management
| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/api/v1/products/` | GET, POST | List/Create products | GET: ❌, POST: ✅ |
| `/api/v1/products/{slug}/` | GET, PUT, DELETE | Product details/update/delete | GET: ❌, Others: ✅ |
| `/api/v1/products/categories/` | GET, POST | Product categories | GET: ❌, POST: ✅ |
| `/api/v1/products/search/` | GET | Advanced product search | ❌ |
| `/api/v1/products/{slug}/reviews/` | GET, POST | Product reviews | GET: ❌, POST: ✅ |


#### Product filtering and sorting
| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/products/?category=category_slug` | GET | Filter by single category | ❌ |
| `/products/?category=category1,category2` | GET | Filter by multiple categories | ❌ |
| `/products/?category=electronics&include_subcategories=false` | GET | Exclude subcategories | ❌ |
| `/products/?category=electronics&min_price=100&max_price=500` | GET | Combine with other filters | ❌ |

#### Order Management
| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/api/v1/orders/` | GET, POST | List/Create orders | ✅ |
| `/api/v1/orders/{id}/` | GET, PUT, DELETE | Order details/update/cancel | ✅ |
| `/api/v1/orders/{id}/status/` | PATCH | Update order status | ✅ (Admin) |
| `/api/v1/cart/` | GET, POST, DELETE | Shopping cart operations | ✅ |
| `/api/v1/cart/items/` | POST, PUT, DELETE | Cart item management | ✅ |
| `/api/v1/cart/checkout/` | POST | Checkout and create order | ✅ |


#### Payment Processing
| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|

| `/api/v1/payments/` | POST | Process payment | ✅ |
| `/api/v1/payments/{id}/` | GET | Payment details | ✅ |
| `/api/v1/payments/` | GET | List payments | ✅ (Admin) |
| `/api/v1/payments/{id}/` | GET | Payment details | ✅ (Admin) |
| `/api/v1/payments/mpesa-payment/` | POST | Initiate M-Pesa payment | ✅ |
| `/api/v1/payments/mpesa-callback/` | POST | M-Pesa callback handler | ❌ |

### 📝 API Usage Examples

#### User Registration
```bash
curl -X POST http://localhost:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "email": "john@example.com",
    "password": "SecurePassword123!",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

#### Create Product (Admin)
```bash
curl -X POST http://localhost:8000/api/v1/products/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_KNOX_TOKEN" \
  -d '{
    "name": "Premium Laptop",
    "description": "High-performance laptop for professionals",
    "price": "1299.99",
    "category": 1,
    "stock_quantity": 50,
    "sku": "LAPTOP-001"
  }'
```

#### Place Order
```bash
curl -X POST http://localhost:8000/api/v1/orders/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_KNOX_TOKEN" \
  -d '{
    "items": [
      {
        "product_id": 1,
        "quantity": 2
      }
    ],
    "shipping_address": {
      "street": "123 Main St",
      "city": "Anytown",
      "state": "CA",
      "zip_code": "12345",
      "country": "US"
    }
=======
#### Place Order (Checkout)
```bash
curl -X POST http://localhost:8000/api/v1/cart/checkout/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_KNOX_TOKEN" \
  -d '{
    "shipping_address": {
      "first_name": "John",
      "last_name": "Doe",
      "company": "Example Corp",
      "address_line_1": "123 Main St",
      "city": "Anytown",
      "state": "CA",
      "postal_code": "12345",
      "country": "US",
      "phone": "+1234567890",
      "email": "john.doe@example.com"
    },
    "payment_method": "mpesa",
    "mpesa_phone_number": "254712345678",
    "customer_notes": "Please deliver in the afternoon."
  }'
```

#### Initiate M-Pesa Payment
After creating an order with the M-Pesa payment method, you can initiate the payment using the following endpoint.

```bash
curl -X POST http://localhost:8000/api/v1/payments/mpesa-payment/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_KNOX_TOKEN" \
  -d '{
    "phone_number": "254712345678",
    "order_id": "YOUR_ORDER_ID"

  }'
```

### 🔄 GraphQL API

Access the GraphQL playground at `http://localhost:8000/graphql/`

#### Sample GraphQL Query
```graphql
query GetProducts($first: Int, $category: String) {
  products(first: $first, category: $category) {
    edges {
      node {
        id
        name
        price
        description
        category {
          name
        }
        reviews {
          rating
          comment
          user {
            username
          }
        }
      }
    }
  }
}
```
