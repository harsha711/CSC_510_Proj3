# SafeBites API Documentation

**Version:** 2.0
**Base URL (Development):** `http://localhost:8000`
**Base URL (Production):** `https://safebites-yu1o.onrender.com`
**Last Updated:** December 2025

---

## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Response Format](#response-format)
4. [Error Handling](#error-handling)
5. [User Endpoints](#user-endpoints)
6. [Restaurant Endpoints](#restaurant-endpoints)
7. [Dish Endpoints](#dish-endpoints)
8. [Data Models](#data-models)
9. [Rate Limiting](#rate-limiting)
10. [Interactive Documentation](#interactive-documentation)

---

## Overview

The SafeBites API is a RESTful API built with FastAPI that provides endpoints for user management, restaurant operations, dish management, and AI-powered conversational menu search.

### Key Features

- **RESTful Design:** Standard HTTP methods (GET, POST, PUT, PATCH, DELETE)
- **JSON Format:** All requests and responses use JSON
- **JWT Authentication:** Secure token-based authentication
- **Auto Documentation:** Interactive API docs at `/docs`
- **Type Validation:** Request/response validation with Pydantic
- **CORS Enabled:** Cross-origin requests supported

### API Conventions

- **Timestamps:** ISO 8601 format (e.g., `2025-12-01T10:30:00Z`)
- **IDs:** MongoDB ObjectId as strings (24 hex characters)
- **Booleans:** `true` or `false` (lowercase)
- **Null values:** Use `null` for missing/empty values

---

## Authentication

SafeBites uses JWT (JSON Web Tokens) for authentication.

### Login Flow

1. **Register** via `POST /users/signup`
2. **Login** via `POST /users/login` to receive JWT token
3. **Include token** in `Authorization` header for protected endpoints

### Token Format

```
Authorization: Bearer <your_jwt_token_here>
```

### Token Expiration

- Tokens expire after 24 hours (configurable)
- Obtain new token by logging in again
- No refresh token mechanism currently

### Protected Endpoints

Endpoints requiring authentication:
- `GET /users/me`
- `PUT /users/me`
- `DELETE /users/me`
- `POST /restaurants/search` (requires user_id)
- All endpoints modifying resources

---

## Response Format

### Success Response

```json
{
  "field1": "value1",
  "field2": "value2",
  ...
}
```

**Status Codes:**
- `200 OK` - Request succeeded
- `201 Created` - Resource created successfully
- `204 No Content` - Successful deletion

### Error Response

```json
{
  "detail": "Error message describing what went wrong",
  "status_code": 400,
  "error_type": "BadRequestException"
}
```

**Status Codes:**
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Missing or invalid authentication
- `404 Not Found` - Resource not found
- `409 Conflict` - Resource already exists
- `422 Unprocessable Entity` - Validation error
- `500 Internal Server Error` - Server error

---

## Error Handling

### Error Types

#### BadRequestException (400)
```json
{
  "detail": "Query cannot be empty",
  "status_code": 400,
  "error_type": "BadRequestException"
}
```

#### UnauthorizedException (401)
```json
{
  "detail": "Invalid credentials",
  "status_code": 401,
  "error_type": "UnauthorizedException"
}
```

#### NotFoundException (404)
```json
{
  "detail": "User not found",
  "status_code": 404,
  "error_type": "NotFoundException"
}
```

#### ValidationError (422)
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

#### GenericException (500)
```json
{
  "detail": "An unexpected error occurred",
  "status_code": 500,
  "error_type": "GenericException"
}
```

---

## User Endpoints

### Register User

Create a new user account.

**Endpoint:** `POST /users/signup`
**Authentication:** None

#### Request Body

```json
{
  "name": "John Doe",
  "username": "johndoe",
  "password": "SecurePassword123!",
  "allergen_preferences": ["peanuts", "dairy", "shellfish"]
}
```

#### Parameters

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | User's full name |
| `username` | string | Yes | Unique username (3-50 chars) |
| `password` | string | Yes | Password (min 8 chars) |
| `allergen_preferences` | array[string] | No | List of allergens to avoid |

**Supported Allergens:**
- `peanuts`
- `tree_nuts`
- `dairy`
- `egg`
- `soy`
- `wheat_gluten`
- `fish`
- `shellfish`
- `sesame`

#### Response (201 Created)

```json
{
  "id": "507f1f77bcf86cd799439011",
  "name": "John Doe",
  "username": "johndoe",
  "allergen_preferences": ["peanuts", "dairy", "shellfish"],
  "created_at": "2025-12-01T10:30:00Z"
}
```

#### Example

```bash
curl -X POST http://localhost:8000/users/signup \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "username": "johndoe",
    "password": "SecurePassword123!",
    "allergen_preferences": ["peanuts", "dairy"]
  }'
```

---

### Login User

Authenticate user and receive JWT token.

**Endpoint:** `POST /users/login`
**Authentication:** None

#### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `username` | string | Yes | User's username |
| `password` | string | Yes | User's password |

#### Response (200 OK)

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "507f1f77bcf86cd799439011",
    "username": "johndoe",
    "name": "John Doe"
  }
}
```

#### Example

```bash
curl -X POST "http://localhost:8000/users/login?username=johndoe&password=SecurePassword123!"
```

---

### Get Current User

Retrieve authenticated user's profile.

**Endpoint:** `GET /users/me`
**Authentication:** Required (Bearer token)

#### Response (200 OK)

```json
{
  "id": "507f1f77bcf86cd799439011",
  "name": "John Doe",
  "username": "johndoe",
  "allergen_preferences": ["peanuts", "dairy", "shellfish"],
  "created_at": "2025-12-01T10:30:00Z"
}
```

#### Example

```bash
curl -X GET http://localhost:8000/users/me \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

### Update User Profile

Update authenticated user's information.

**Endpoint:** `PUT /users/me`
**Authentication:** Required (Bearer token)

#### Request Body

```json
{
  "name": "John Smith",
  "allergen_preferences": ["peanuts", "shellfish"]
}
```

#### Parameters

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | No | Updated name |
| `username` | string | No | Updated username |
| `password` | string | No | Updated password |
| `allergen_preferences` | array[string] | No | Updated allergen list |

#### Response (200 OK)

```json
{
  "id": "507f1f77bcf86cd799439011",
  "name": "John Smith",
  "username": "johndoe",
  "allergen_preferences": ["peanuts", "shellfish"],
  "created_at": "2025-12-01T10:30:00Z"
}
```

#### Example

```bash
curl -X PUT http://localhost:8000/users/me \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Smith",
    "allergen_preferences": ["peanuts"]
  }'
```

---

### Delete User Account

Delete authenticated user's account.

**Endpoint:** `DELETE /users/me`
**Authentication:** Required (Bearer token)

#### Response (200 OK)

```json
{
  "message": "User deleted successfully"
}
```

#### Example

```bash
curl -X DELETE http://localhost:8000/users/me \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

### Get User by ID or Username

Retrieve user information by ID or username.

**Endpoint:** `GET /users/{id_or_username}`
**Authentication:** None

#### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `id_or_username` | string | User ID (ObjectId) or username |

#### Response (200 OK)

```json
{
  "id": "507f1f77bcf86cd799439011",
  "name": "John Doe",
  "username": "johndoe",
  "allergen_preferences": ["peanuts", "dairy"],
  "created_at": "2025-12-01T10:30:00Z"
}
```

#### Example

```bash
# By ID
curl -X GET http://localhost:8000/users/507f1f77bcf86cd799439011

# By username
curl -X GET http://localhost:8000/users/johndoe
```

---

## Restaurant Endpoints

### Create Restaurant

Create a new restaurant with optional menu CSV upload.

**Endpoint:** `POST /restaurants/`
**Authentication:** Required (Bearer token)
**Content-Type:** `multipart/form-data`

#### Form Data

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Restaurant name |
| `location` | string | Yes | Restaurant address/location |
| `cuisine` | array[string] | No | Cuisine types (e.g., ["Italian", "Pizza"]) |
| `rating` | float | No | Rating (0.0 - 5.0) |
| `menu_file` | file | No | CSV file with menu items |

#### CSV Format

```csv
dish_name,description,price,ingredients,allergens,nutrition_facts
Margherita Pizza,Classic tomato and cheese,12.99,"tomato,cheese,basil","dairy,gluten","{calories:250}"
Caesar Salad,Fresh romaine with caesar dressing,8.99,"romaine,parmesan,croutons","dairy,egg","{calories:180}"
```

**CSV Columns:**
- `dish_name` (required): Name of the dish
- `description` (optional): Dish description
- `price` (required): Price as decimal number
- `ingredients` (optional): Comma-separated ingredients
- `allergens` (optional): Comma-separated allergens
- `nutrition_facts` (optional): JSON string with nutrition data

#### Response (201 Created)

```json
{
  "id": "507f1f77bcf86cd799439012",
  "name": "Mama's Italian Kitchen",
  "location": "123 Main St, Raleigh, NC",
  "cuisine": ["Italian", "Pizza"],
  "rating": 4.5,
  "created_at": "2025-12-01T10:30:00Z",
  "dish_count": 25
}
```

#### Example

```bash
curl -X POST http://localhost:8000/restaurants/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "name=Mama's Italian Kitchen" \
  -F "location=123 Main St, Raleigh, NC" \
  -F "cuisine=Italian,Pizza" \
  -F "rating=4.5" \
  -F "menu_file=@menu.csv"
```

---

### List All Restaurants

Retrieve all restaurants.

**Endpoint:** `GET /restaurants/`
**Authentication:** None

#### Response (200 OK)

```json
[
  {
    "id": "507f1f77bcf86cd799439012",
    "name": "Mama's Italian Kitchen",
    "location": "123 Main St, Raleigh, NC",
    "cuisine": ["Italian", "Pizza"],
    "rating": 4.5,
    "created_at": "2025-12-01T10:30:00Z"
  },
  {
    "id": "507f1f77bcf86cd799439013",
    "name": "Thai Spice House",
    "location": "456 Oak Ave, Raleigh, NC",
    "cuisine": ["Thai", "Asian"],
    "rating": 4.7,
    "created_at": "2025-12-01T11:00:00Z"
  }
]
```

#### Example

```bash
curl -X GET http://localhost:8000/restaurants/
```

---

### Get Restaurant Details

Retrieve details for a specific restaurant.

**Endpoint:** `GET /restaurants/{restaurant_id}`
**Authentication:** None

#### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `restaurant_id` | string | Restaurant ID (ObjectId) |

#### Response (200 OK)

```json
{
  "id": "507f1f77bcf86cd799439012",
  "name": "Mama's Italian Kitchen",
  "location": "123 Main St, Raleigh, NC",
  "cuisine": ["Italian", "Pizza"],
  "rating": 4.5,
  "created_at": "2025-12-01T10:30:00Z",
  "menu_items": [
    {
      "dish_id": "507f1f77bcf86cd799439014",
      "dish_name": "Margherita Pizza",
      "price": 12.99
    }
  ]
}
```

#### Example

```bash
curl -X GET http://localhost:8000/restaurants/507f1f77bcf86cd799439012
```

---

### Update Restaurant

Update restaurant information.

**Endpoint:** `PATCH /restaurants/{restaurant_id}`
**Authentication:** Required (Bearer token)

#### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `restaurant_id` | string | Restaurant ID (ObjectId) |

#### Request Body

```json
{
  "name": "Mama's Italian Restaurant",
  "rating": 4.8
}
```

#### Parameters

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | No | Updated name |
| `location` | string | No | Updated location |
| `cuisine` | array[string] | No | Updated cuisine types |
| `rating` | float | No | Updated rating (0.0 - 5.0) |

#### Response (200 OK)

```json
{
  "id": "507f1f77bcf86cd799439012",
  "name": "Mama's Italian Restaurant",
  "location": "123 Main St, Raleigh, NC",
  "cuisine": ["Italian", "Pizza"],
  "rating": 4.8,
  "created_at": "2025-12-01T10:30:00Z"
}
```

#### Example

```bash
curl -X PATCH http://localhost:8000/restaurants/507f1f77bcf86cd799439012 \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Mama'\''s Italian Restaurant",
    "rating": 4.8
  }'
```

---

### Delete Restaurant

Delete a restaurant and all its dishes.

**Endpoint:** `DELETE /restaurants/{restaurant_id}`
**Authentication:** Required (Bearer token)

#### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `restaurant_id` | string | Restaurant ID (ObjectId) |

#### Response (200 OK)

```json
{
  "message": "Restaurant deleted successfully",
  "dishes_deleted": 25
}
```

#### Example

```bash
curl -X DELETE http://localhost:8000/restaurants/507f1f77bcf86cd799439012 \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

### AI-Powered Chat Search

Execute conversational menu search using LangGraph pipeline.

**Endpoint:** `POST /restaurants/search`
**Authentication:** Required (user_id must match authenticated user)

#### Request Body

```json
{
  "query": "Show me vegan pizzas under $15",
  "user_id": "507f1f77bcf86cd799439011",
  "restaurant_id": "507f1f77bcf86cd799439012",
  "session_id": "session_abc123"
}
```

#### Parameters

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `query` | string | Yes | Natural language query |
| `user_id` | string | Yes | User ID (must match auth) |
| `restaurant_id` | string | Yes | Restaurant to search |
| `session_id` | string | No | Session ID for context (auto-generated if missing) |

#### Response (200 OK)

```json
{
  "user_id": "507f1f77bcf86cd799439011",
  "session_id": "session_abc123",
  "restaurant_id": "507f1f77bcf86cd799439012",
  "original_query": "Show me vegan pizzas under $15",
  "responses": [
    {
      "query": "vegan pizzas under $15",
      "type": "menu_search",
      "result": [
        {
          "dish_id": "507f1f77bcf86cd799439014",
          "dish_name": "Vegan Margherita",
          "description": "Classic pizza with vegan cheese",
          "price": 12.99,
          "ingredients": ["tomato sauce", "vegan cheese", "basil"],
          "allergens": [
            {
              "allergen": "soy",
              "confidence": 0.9,
              "why": "Vegan cheese typically contains soy"
            }
          ],
          "nutrition_facts": {
            "calories": {"value": 220, "confidence": 0.85},
            "protein": {"value": 8, "confidence": 0.8},
            "fat": {"value": 7, "confidence": 0.8}
          },
          "safe_for_user": true
        }
      ]
    }
  ],
  "status": "success",
  "timestamp": "2025-12-01T10:30:00Z"
}
```

#### Response Structure

**Response Types:**
- `menu_search` - Dish listings from semantic search
- `dish_info` - Detailed information about specific dishes
- `user_preferences` - User's allergen preferences
- `irrelevant` - Unrelated query

**Dish Result Fields:**
- `dish_id` - Unique dish identifier
- `dish_name` - Name of the dish
- `description` - Dish description
- `price` - Price in USD
- `ingredients` - List of ingredients
- `allergens` - Array of allergen objects with confidence scores
- `nutrition_facts` - Nutrition information with confidence scores
- `safe_for_user` - Boolean indicating safety for user's allergens

#### Example Queries

**Simple Menu Search:**
```json
{
  "query": "Show me all pasta dishes"
}
```

**Multi-Intent Query:**
```json
{
  "query": "Show me vegan options and tell me the calories in the Caesar salad"
}
```

**Contextual Follow-up:**
```json
{
  "query": "What about under $10?"
}
```

**Dish Information:**
```json
{
  "query": "What are the ingredients in the margherita pizza?"
}
```

**User Preferences:**
```json
{
  "query": "What am I allergic to?"
}
```

#### Example

```bash
curl -X POST http://localhost:8000/restaurants/search \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Show me vegan pizzas under $15",
    "user_id": "507f1f77bcf86cd799439011",
    "restaurant_id": "507f1f77bcf86cd799439012"
  }'
```

---

### Get Chat History

Retrieve conversation history for a user-restaurant session.

**Endpoint:** `GET /restaurants/history/{user_id}/{restaurant_id}`
**Authentication:** Required (user_id must match authenticated user)

#### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `user_id` | string | User ID (ObjectId) |
| `restaurant_id` | string | Restaurant ID (ObjectId) |

#### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | integer | 50 | Maximum messages to return |
| `offset` | integer | 0 | Number of messages to skip |

#### Response (200 OK)

```json
{
  "user_id": "507f1f77bcf86cd799439011",
  "restaurant_id": "507f1f77bcf86cd799439012",
  "total_messages": 10,
  "messages": [
    {
      "session_id": "session_abc123",
      "query": "Show me vegan pizzas",
      "response": { /* full response object */ },
      "timestamp": "2025-12-01T10:30:00Z"
    },
    {
      "session_id": "session_abc123",
      "query": "Under $15?",
      "response": { /* full response object */ },
      "timestamp": "2025-12-01T10:31:00Z"
    }
  ]
}
```

#### Example

```bash
curl -X GET "http://localhost:8000/restaurants/history/507f1f77bcf86cd799439011/507f1f77bcf86cd799439012?limit=20" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## Dish Endpoints

### Create Dish

Add a new dish to a restaurant.

**Endpoint:** `POST /dishes/{restaurant_id}`
**Authentication:** Required (Bearer token)

#### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `restaurant_id` | string | Restaurant ID (ObjectId) |

#### Request Body

```json
{
  "dish_name": "Spicy Thai Curry",
  "description": "Red curry with vegetables and tofu",
  "price": 14.99,
  "ingredients": ["coconut milk", "curry paste", "tofu", "vegetables"],
  "explicit_allergens": [
    {
      "allergen": "soy",
      "confidence": 1.0,
      "why": "Contains tofu (soy product)"
    },
    {
      "allergen": "tree_nuts",
      "confidence": 0.8,
      "why": "May contain peanuts in curry paste"
    }
  ],
  "nutrition_facts": {
    "calories": {"value": 320, "confidence": 0.9},
    "protein": {"value": 12, "confidence": 0.85},
    "fat": {"value": 18, "confidence": 0.85},
    "carbohydrates": {"value": 28, "confidence": 0.85}
  },
  "serving_size": "1 bowl (350g)",
  "availability": true
}
```

#### Parameters

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `dish_name` | string | Yes | Name of the dish |
| `description` | string | No | Dish description |
| `price` | float | Yes | Price in USD |
| `ingredients` | array[string] | No | List of ingredients |
| `explicit_allergens` | array[object] | No | Allergen information |
| `nutrition_facts` | object | No | Nutrition information |
| `serving_size` | string | No | Serving size description |
| `availability` | boolean | No | Availability status (default: true) |

#### Response (201 Created)

```json
{
  "dish_id": "507f1f77bcf86cd799439014",
  "restaurant_id": "507f1f77bcf86cd799439012",
  "dish_name": "Spicy Thai Curry",
  "description": "Red curry with vegetables and tofu",
  "price": 14.99,
  "ingredients": ["coconut milk", "curry paste", "tofu", "vegetables"],
  "explicit_allergens": [
    {
      "allergen": "soy",
      "confidence": 1.0,
      "why": "Contains tofu (soy product)"
    }
  ],
  "nutrition_facts": {
    "calories": {"value": 320, "confidence": 0.9}
  },
  "serving_size": "1 bowl (350g)",
  "availability": true,
  "created_at": "2025-12-01T10:30:00Z"
}
```

#### Example

```bash
curl -X POST http://localhost:8000/dishes/507f1f77bcf86cd799439012 \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "dish_name": "Spicy Thai Curry",
    "price": 14.99,
    "ingredients": ["coconut milk", "curry paste", "tofu", "vegetables"]
  }'
```

---

### List Dishes

Retrieve all dishes with optional filters.

**Endpoint:** `GET /dishes/`
**Authentication:** None

#### Query Parameters

| Parameter | Type | Description |
|-----------|------|----------|
| `restaurant_id` | string | Filter by restaurant ID |
| `min_price` | float | Minimum price |
| `max_price` | float | Maximum price |
| `available_only` | boolean | Show only available dishes (default: false) |
| `limit` | integer | Max results (default: 100) |
| `offset` | integer | Skip N results (default: 0) |

#### Response (200 OK)

```json
{
  "total": 150,
  "limit": 100,
  "offset": 0,
  "dishes": [
    {
      "dish_id": "507f1f77bcf86cd799439014",
      "restaurant_id": "507f1f77bcf86cd799439012",
      "dish_name": "Margherita Pizza",
      "price": 12.99,
      "availability": true
    }
  ]
}
```

#### Example

```bash
# All dishes
curl -X GET http://localhost:8000/dishes/

# Filtered by restaurant and price
curl -X GET "http://localhost:8000/dishes/?restaurant_id=507f1f77bcf86cd799439012&max_price=15"
```

---

### Filter Dishes by Allergens

Filter dishes by allergen-free criteria.

**Endpoint:** `GET /dishes/filter`
**Authentication:** None

#### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `restaurant_id` | string | No | Filter by restaurant |
| `allergens` | string | Yes | Comma-separated allergen list |

#### Response (200 OK)

```json
{
  "restaurant_id": "507f1f77bcf86cd799439012",
  "allergens_excluded": ["peanuts", "dairy"],
  "safe_dishes": [
    {
      "dish_id": "507f1f77bcf86cd799439014",
      "dish_name": "Vegan Buddha Bowl",
      "price": 11.99,
      "allergens": ["soy"],
      "safe": true
    }
  ]
}
```

#### Example

```bash
curl -X GET "http://localhost:8000/dishes/filter?allergens=peanuts,dairy&restaurant_id=507f1f77bcf86cd799439012"
```

---

### Get Dish Details

Retrieve detailed information for a specific dish.

**Endpoint:** `GET /dishes/{dish_id}`
**Authentication:** None

#### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `dish_id` | string | Dish ID (ObjectId) |

#### Response (200 OK)

```json
{
  "dish_id": "507f1f77bcf86cd799439014",
  "restaurant_id": "507f1f77bcf86cd799439012",
  "dish_name": "Margherita Pizza",
  "description": "Classic tomato and mozzarella pizza",
  "price": 12.99,
  "ingredients": ["tomato sauce", "mozzarella", "basil", "olive oil"],
  "explicit_allergens": [
    {
      "allergen": "dairy",
      "confidence": 1.0,
      "why": "Contains mozzarella cheese"
    },
    {
      "allergen": "wheat_gluten",
      "confidence": 0.95,
      "why": "Pizza dough contains wheat flour"
    }
  ],
  "nutrition_facts": {
    "calories": {"value": 250, "confidence": 0.9},
    "protein": {"value": 12, "confidence": 0.85},
    "fat": {"value": 9, "confidence": 0.85},
    "carbohydrates": {"value": 30, "confidence": 0.85},
    "sugar": {"value": 3, "confidence": 0.8},
    "fiber": {"value": 2, "confidence": 0.8}
  },
  "serving_size": "1 slice (120g)",
  "availability": true,
  "created_at": "2025-12-01T10:30:00Z"
}
```

#### Example

```bash
curl -X GET http://localhost:8000/dishes/507f1f77bcf86cd799439014
```

---

### Update Dish

Update dish information.

**Endpoint:** `PUT /dishes/{dish_id}`
**Authentication:** Required (Bearer token)

#### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `dish_id` | string | Dish ID (ObjectId) |

#### Request Body

```json
{
  "price": 13.99,
  "availability": false,
  "description": "Updated description"
}
```

#### Parameters

All dish fields are optional. Only provided fields will be updated.

#### Response (200 OK)

Returns updated dish object (same structure as GET /dishes/{dish_id})

#### Example

```bash
curl -X PUT http://localhost:8000/dishes/507f1f77bcf86cd799439014 \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "price": 13.99,
    "availability": false
  }'
```

---

### Delete Dish

Delete a dish from the restaurant.

**Endpoint:** `DELETE /dishes/{dish_id}`
**Authentication:** Required (Bearer token)

#### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `dish_id` | string | Dish ID (ObjectId) |

#### Response (200 OK)

```json
{
  "message": "Dish deleted successfully",
  "dish_id": "507f1f77bcf86cd799439014"
}
```

#### Example

```bash
curl -X DELETE http://localhost:8000/dishes/507f1f77bcf86cd799439014 \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## Data Models

### User

```typescript
{
  id: string,                    // MongoDB ObjectId
  name: string,                  // User's full name
  username: string,              // Unique username
  allergen_preferences: string[], // List of allergens
  created_at: string             // ISO 8601 timestamp
}
```

### Restaurant

```typescript
{
  id: string,                    // MongoDB ObjectId
  name: string,                  // Restaurant name
  location: string,              // Address/location
  cuisine: string[],             // Cuisine types
  rating: number,                // 0.0 - 5.0
  created_at: string             // ISO 8601 timestamp
}
```

### Dish

```typescript
{
  dish_id: string,               // MongoDB ObjectId
  restaurant_id: string,         // Restaurant ObjectId
  dish_name: string,             // Dish name
  description: string,           // Dish description
  price: number,                 // Price in USD
  ingredients: string[],         // List of ingredients
  explicit_allergens: AllergenInfo[], // Allergen data
  nutrition_facts: NutritionFacts,    // Nutrition data
  serving_size: string,          // Serving size description
  availability: boolean,         // Availability status
  created_at: string             // ISO 8601 timestamp
}
```

### AllergenInfo

```typescript
{
  allergen: string,              // Allergen type
  confidence: number,            // 0.0 - 1.0
  why: string                    // Explanation
}
```

**Allergen Types:**
- `peanuts`
- `tree_nuts`
- `dairy`
- `egg`
- `soy`
- `wheat_gluten`
- `fish`
- `shellfish`
- `sesame`

### NutritionFacts

```typescript
{
  calories: { value: number, confidence: number },
  protein: { value: number, confidence: number },
  fat: { value: number, confidence: number },
  carbohydrates: { value: number, confidence: number },
  sugar: { value: number, confidence: number },
  fiber: { value: number, confidence: number }
}
```

**Units:**
- `calories`: kcal
- `protein`, `fat`, `carbohydrates`, `sugar`, `fiber`: grams (g)

### ChatState

```typescript
{
  user_id: string,               // User ObjectId
  session_id: string,            // Session identifier
  restaurant_id: string,         // Restaurant ObjectId
  query: string,                 // User's query
  intents: IntentExtractionResult, // Extracted intents
  context: string[],             // Conversation history
  query_parts: QueryParts,       // Organized query parts
  menu_results: object,          // Menu search results
  info_results: object,          // Dish info results
  preference_results: object,    // User preference results
  response: string,              // Final response
  status: string,                // "success" | "failed"
  timestamp: string              // ISO 8601 timestamp
}
```

### IntentExtractionResult

```typescript
{
  intents: IntentQuery[]         // Array of extracted intents
}
```

### IntentQuery

```typescript
{
  type: string,                  // Intent type
  query: string                  // Query text
}
```

**Intent Types:**
- `menu_search` - Dish listing queries
- `dish_info` - Detailed dish information
- `user_preferences` - User allergen preferences
- `irrelevant` - Unrelated queries

---

## Rate Limiting

Currently, there is no rate limiting enforced on the API. However, best practices recommend:

- Maximum 100 requests per minute per IP
- Maximum 1000 requests per hour per user
- Burst limit of 20 requests per second

**Note:** Rate limiting will be implemented in future versions.

---

## Interactive Documentation

SafeBites API provides interactive documentation using Swagger UI and ReDoc.

### Swagger UI

**URL:** `http://localhost:8000/docs` (development)
**URL:** `https://safebites-yu1o.onrender.com/docs` (production)

Features:
- Interactive API explorer
- Try out endpoints directly
- Request/response examples
- Schema definitions
- Authentication support

### ReDoc

**URL:** `http://localhost:8000/redoc` (development)
**URL:** `https://safebites-yu1o.onrender.com/redoc` (production)

Features:
- Clean, readable documentation
- Searchable interface
- Code samples
- Detailed schema documentation

### OpenAPI Specification

**URL:** `http://localhost:8000/openapi.json`

Download the OpenAPI 3.0 specification in JSON format for:
- Importing into Postman
- Generating client SDKs
- API testing tools
- Documentation generators

---

## Code Examples

### Python (requests)

```python
import requests

# Base URL
BASE_URL = "http://localhost:8000"

# Register user
response = requests.post(
    f"{BASE_URL}/users/signup",
    json={
        "name": "John Doe",
        "username": "johndoe",
        "password": "SecurePassword123!",
        "allergen_preferences": ["peanuts", "dairy"]
    }
)
user = response.json()
print(f"User created: {user['id']}")

# Login
response = requests.post(
    f"{BASE_URL}/users/login",
    params={"username": "johndoe", "password": "SecurePassword123!"}
)
token = response.json()["access_token"]
print(f"Token: {token}")

# Chat search
headers = {"Authorization": f"Bearer {token}"}
response = requests.post(
    f"{BASE_URL}/restaurants/search",
    headers=headers,
    json={
        "query": "Show me vegan pizzas under $15",
        "user_id": user["id"],
        "restaurant_id": "507f1f77bcf86cd799439012"
    }
)
results = response.json()
print(f"Found {len(results['responses'])} results")
```

### JavaScript (fetch)

```javascript
const BASE_URL = "http://localhost:8000";

// Register user
const registerUser = async () => {
  const response = await fetch(`${BASE_URL}/users/signup`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      name: "John Doe",
      username: "johndoe",
      password: "SecurePassword123!",
      allergen_preferences: ["peanuts", "dairy"]
    })
  });
  const user = await response.json();
  console.log("User created:", user.id);
  return user;
};

// Login
const loginUser = async () => {
  const response = await fetch(
    `${BASE_URL}/users/login?username=johndoe&password=SecurePassword123!`,
    { method: "POST" }
  );
  const data = await response.json();
  console.log("Token:", data.access_token);
  return data.access_token;
};

// Chat search
const searchMenu = async (token, userId, restaurantId) => {
  const response = await fetch(`${BASE_URL}/restaurants/search`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`
    },
    body: JSON.stringify({
      query: "Show me vegan pizzas under $15",
      user_id: userId,
      restaurant_id: restaurantId
    })
  });
  const results = await response.json();
  console.log("Results:", results);
  return results;
};
```

### cURL Examples

See individual endpoint sections for cURL examples.

---

## Changelog

### Version 2.0 (December 2025)
- Added LangGraph-based conversational search
- Implemented multi-intent query support
- Added context resolution across conversation turns
- Enhanced allergen detection with confidence scoring
- Added nutrition facts with confidence tracking
- Implemented session-based chat history
- Added user preference queries
- Improved error handling and validation

### Version 1.0 (November 2025)
- Initial API release
- Basic CRUD operations for users, restaurants, dishes
- JWT authentication
- CSV menu upload
- Simple search functionality

---

## Support & Feedback

For API-related questions, issues, or feedback:

- **GitHub Issues:** [Create an issue](https://github.com/yourusername/safebites/issues)
- **Email:** api-support@safebites.com
- **Documentation:** [Full docs](https://github.com/yourusername/safebites/tree/main/docs)

---

**Last Updated:** December 2025
**API Version:** 2.0
**Documentation Version:** 2.0.0
