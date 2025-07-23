# Product Management API Documentation

## Table of Contents
1. [Overview](#overview)
2. [API Endpoints](#api-endpoints)
3. [Data Models](#data-models)
4. [Authentication & Permissions](#authentication--permissions)
5. [Filtering & Searching](#filtering--searching)
6. [Pagination](#pagination)
7. [Examples](#examples)
8. [Error Handling](#error-handling)

## Overview

The Product Management API provides comprehensive functionality for managing an e-commerce product catalog, including:

- Hierarchical category management
- Brand management
- Product listings with variants
- Product images and specifications
- Customer reviews and ratings
- Inventory tracking

All endpoints return JSON responses and follow RESTful conventions.

## API Endpoints

### Categories
| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/categories/` | GET | List all root categories | No |
| `/categories/` | POST | Create new category | Yes |
| `/categories/{slug}/` | GET | Get category details | No |
| `/categories/{slug}/children/` | GET | Get child categories | No |
| `/categories/{slug}/` | PUT/PATCH | Update category | Yes |
| `/categories/{slug}/` | DELETE | Delete category | Yes |

### Brands
| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/brands/` | GET | List all brands | No |
| `/brands/` | POST | Create new brand | Yes |
| `/brands/{slug}/` | GET | Get brand details | No |
| `/brands/{slug}/` | PUT/PATCH | Update brand | Yes |
| `/brands/{slug}/` | DELETE | Delete brand | Yes |

### Products
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

### Product Variants
| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/product-variants/` | GET | List variants | Yes |
| `/product-variants/` | POST | Create variant | Yes |
| `/product-variants/{id}/` | GET | Get variant details | Yes |
| `/product-variants/{id}/` | PUT/PATCH | Update variant | Yes |
| `/product-variants/{id}/` | DELETE | Delete variant | Yes |

## Data Models

### Category
```json
{
  "id": 1,
  "name": "Electronics",
  "slug": "electronics",
  "parent": null,
  "description": "All electronic devices",
  "is_active": true,
  "full_path": "Electronics",
  "product_count": 42,
  "created_at": "2023-01-15T10:30:00Z",
  "updated_at": "2023-01-15T10:30:00Z"
}
```

### Brand
```json
{
  "id": 1,
  "name": "TechCorp",
  "slug": "techcorp",
  "description": "Leading tech manufacturer",
  "logo_url": "https://example.com/media/brands/logos/techcorp.png",
  "is_active": true,
  "website": "https://techcorp.com",
  "product_count": 15,
  "created_at": "2023-01-10T09:15:00Z",
  "updated_at": "2023-01-10T09:15:00Z"
}
```

### Product
```json
{
  "id": 123,
  "name": "Premium Smartphone",
  "slug": "premium-smartphone",
  "description": "Latest model with advanced features",
  "category": {...},
  "brand": {...},
  "status": "active",
  "price": "799.99",
  "compare_at_price": "899.99",
  "discount_percentage": "11.11",
  "sku": "SMARTPH-001",
  "quantity": 50,
  "inventory_status": "in_stock",
  "is_featured": true,
  "primary_image": {...},
  "images": [...],
  "variants": [...],
  "specifications": [...],
  "reviews": [...],
  "average_rating": "4.5"
}
```

## Authentication & Permissions

- **Public Access**: Read-only endpoints (GET) for categories, brands, products
- **Authenticated Users**: Can submit product reviews
- **Staff Users**: Full CRUD access to all models
- **Permissions**: Managed via DjangoModelPermissions (view/add/change/delete)

## Filtering & Searching

All list endpoints support:

### Common Filters
- `search`: Full-text search across relevant fields
- `ordering`: Sort by any model field (`?ordering=-price`)
- `page_size`: Items per page (default 24, max 100)

### Product-Specific Filters
- `min_price` / `max_price`: Price range filtering
- `category`: Filter by category slug
- `brand`: Filter by brand slug
- `status`: Filter by product status
- `featured`: Filter featured products

Example:
```
/products/?category=electronics&min_price=100&max_price=500&ordering=-average_rating
```

## Pagination

All list endpoints use optimized pagination:

```json
{
  "links": {
    "next": "https://api.example.com/products/?page=2",
    "previous": null
  },
  "count": 120,
  "page_size": 24,
  "results": [...]
}
```

## Examples

### Create a Product
```http
POST /products/
Content-Type: application/json
Authorization: Token your-auth-token

{
  "name": "New Product",
  "description": "Product description",
  "category_id": 1,
  "brand_id": 1,
  "price": "99.99",
  "sku": "PROD-001",
  "quantity": 100
}
```

### Add Product Review
```http
POST /products/premium-smartphone/add-review/
Content-Type: application/json
Authorization: Token your-auth-token

{
  "rating": 5,
  "title": "Excellent phone",
  "comment": "Great battery life and camera quality"
}
```

## Error Handling

Common error responses:

- **400 Bad Request**: Invalid input data
- **401 Unauthorized**: Missing/invalid authentication
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Resource doesn't exist
- **429 Too Many Requests**: Rate limit exceeded

Error response format:
```json
{
  "detail": "Error message",
  "code": "error_code",
  "errors": {
    "field": ["Specific error about field"]
  }
}
```
