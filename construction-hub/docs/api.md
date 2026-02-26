# API Documentation for Construction Hub

## Overview
The Construction Hub API allows customers to order construction products from suppliers, consult about building plans and costs, and receive planning services. The API is designed to support different user roles: admin, customers, and suppliers.

## Authentication
All API requests require authentication. Users must obtain a token by logging in with their credentials.

### Login
- **Endpoint:** `/api/login/`
- **Method:** POST
- **Request Body:**
  - `username`: string
  - `password`: string
- **Response:**
  - `token`: string

## User Roles
### Admin
- Can manage users, products, orders, and consultations.

### Customers
- Can view products, make orders, and apply for consultations.

### Suppliers
- Can post construction materials with costs and locations.

## Endpoints

### Products
- **Get All Products**
  - **Endpoint:** `/api/products/`
  - **Method:** GET
  - **Response:** List of products with details (name, cost, location).

- **Create Product**
  - **Endpoint:** `/api/products/`
  - **Method:** POST
  - **Request Body:**
    - `name`: string
    - `cost`: decimal
    - `location`: string
  - **Response:** Created product details.

### Orders
- **Create Order**
  - **Endpoint:** `/api/orders/`
  - **Method:** POST
  - **Request Body:**
    - `product_id`: integer
    - `quantity`: integer
  - **Response:** Order confirmation details.

### Consultations
- **Request Consultation**
  - **Endpoint:** `/api/consultations/`
  - **Method:** POST
  - **Request Body:**
    - `details`: string
  - **Response:** Consultation request confirmation.

### User Dashboard
- **Get User Dashboard**
  - **Endpoint:** `/api/dashboard/`
  - **Method:** GET
  - **Response:** User-specific data including orders and consultations.

## Error Handling
The API returns standard HTTP status codes to indicate the success or failure of requests. Common error responses include:
- **400 Bad Request:** Invalid input data.
- **401 Unauthorized:** Authentication required.
- **404 Not Found:** Resource not found.
- **500 Internal Server Error:** Unexpected server error.

## Rate Limiting
To ensure fair usage, the API implements rate limiting. Users are limited to a certain number of requests per minute.

## Conclusion
This API documentation provides a comprehensive overview of the endpoints available in the Construction Hub project. For further details, please refer to the individual endpoint documentation or the source code.