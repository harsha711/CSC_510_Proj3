# SafeBites Features Documentation

## Table of Contents
1. [Overview](#overview)
2. [Core Features](#core-features)
3. [AI & Machine Learning Features](#ai--machine-learning-features)
4. [User Management Features](#user-management-features)
5. [Restaurant & Menu Management](#restaurant--menu-management)
6. [Search & Discovery](#search--discovery)
7. [Safety & Allergen Features](#safety--allergen-features)
8. [API Features](#api-features)
9. [Frontend Features](#frontend-features)
10. [Future Roadmap](#future-roadmap)

---

## Overview

SafeBites is an intelligent food delivery and menu search platform that combines conversational AI, semantic search, and allergen safety features to help users discover and understand restaurant menus through natural language conversations.

**Current Version:** Project 3
**Status:** In Production
**Last Updated:** December 2025

---

## Core Features

### 1. Conversational AI Menu Search
**Status:** ✅ Implemented

An advanced AI-powered search system that understands natural language queries and maintains context across multiple conversation turns.

**Capabilities:**
- Natural language query processing
- Multi-turn conversation support
- Context-aware responses
- Complex query handling (multiple intents in one message)
- Implicit reference resolution ("that dish", "the pasta", etc.)

**Example Queries:**
```
✓ "Show me vegan pizzas under $15"
✓ "What about something with high protein?"
✓ "List dishes without peanuts and dairy"
✓ "Tell me the calories in the margherita pizza"
✓ "What am I allergic to?"
```

**Technical Implementation:**
- LangGraph pipeline with 7 processing nodes
- GPT-4o-mini for intent extraction
- Context resolution using conversation history
- State persistence in MongoDB
- Session-based conversation tracking

---

### 2. Semantic Search with FAISS
**Status:** Pending

Advanced vector-based semantic search that understands meaning beyond keyword matching.

**Features:**
- Vector embeddings using OpenAI text-embedding-3-large (1536 dimensions)
- Semantic similarity matching
- Positive and negative intent filtering
- Restaurant-specific index filtering
- Dynamic filter application (price, ingredients, allergens)

**How It Works:**
1. User query converted to vector embedding
2. FAISS performs k-nearest neighbor search
3. Negative intents filter out unwanted results
4. Additional filters applied (price, allergens, ingredients)
5. Results ranked by semantic similarity

**Example:**
```
Query: "creamy pasta without seafood"
→ Finds: "Fettuccine Alfredo", "Carbonara", "Mac and Cheese"
→ Filters out: "Seafood Linguine", "Shrimp Pasta"
```

---

### 3. Intent Classification System
**Status:** ✅ Implemented

Automatically classifies user queries into actionable intent types for precise response generation.

**Supported Intent Types:**

#### a) Menu Search (`menu_search`)
Queries requesting dish listings or specific items from the menu.

**Examples:**
- "Show me all vegan options"
- "List pizzas under $20"
- "What pasta dishes do you have?"

#### b) Dish Information (`dish_info`)
Queries requesting detailed information about specific dishes.

**Examples:**
- "What are the ingredients in the Caesar salad?"
- "How many calories in the veggie burger?"
- "Does the pizza contain gluten?"

#### c) User Preferences (`user_preferences`)
Queries about user's own allergen preferences or account settings.

**Examples:**
- "What am I allergic to?"
- "What are my dietary restrictions?"
- "Show my allergen list"

#### d) Irrelevant (`irrelevant`)
Queries unrelated to food, menus, or the restaurant.

**Examples:**
- "What's the weather today?"
- "Tell me a joke"

**Multi-Intent Handling:**
Single queries can contain multiple intents, each processed independently:
```
"Show me vegan pizzas and tell me the calories in the margherita"
→ Intent 1: menu_search for vegan pizzas
→ Intent 2: dish_info for margherita calories
```

---

### 4. Context Resolution
**Status:** ✅ Implemented

Resolves implicit references and maintains conversation coherence across multiple turns.

**Capabilities:**
- Anaphora resolution ("it", "that", "those", "the dish")
- Context summarization from conversation history
- Query rewriting for clarity
- Special handling for user preference queries

**Example Conversation:**
```
User: "Show me pizzas"
Bot: [Lists 10 pizzas]

User: "What about under $15?"
→ Resolved to: "Show me pizzas under $15"

User: "Tell me about that margherita"
→ Resolved to: "Tell me about the margherita pizza"
```

**Technical Details:**
- Uses GPT-4 for query rewriting
- Analyzes last 5 conversation turns
- Produces self-contained queries
- Generates context summaries (<300 words)

---

## AI & Machine Learning Features

### 5. LangGraph Conversation Pipeline
**Status:** ✅ Implemented

A sophisticated state machine orchestrating the entire conversation flow.

**Pipeline Architecture:**

```
┌─────────────────────┐
│  User Query Input   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Context Resolver    │ → Rewrites query with references resolved
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Intent Classifier   │ → Extracts 4 intent types
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Query Part Gen.     │ → Organizes intents by type
└──────────┬──────────┘
           │
     ┌─────┴─────┐
     ▼           ▼
┌─────────┐  ┌────────────┐
│  Menu   │  │ Dish Info  │ → Parallel retrieval
│Retriever│  │ Retriever  │
└────┬────┘  └─────┬──────┘
     │            │
     └──────┬─────┘
            ▼
    ┌───────────────┐
    │   Response    │ → Formats final output
    │  Synthesizer  │
    └───────────────┘
```

**Node Functions:**
1. **context_resolver:** Resolves references and summarizes context
2. **intent_classifier:** Extracts and categorizes user intents
3. **query_part_generator:** Organizes intents into structured queries
4. **menu_retriever:** Performs semantic search for dishes
5. **informative_retriever:** Retrieves detailed dish information
6. **user_preferences_retriever:** Handles user-specific queries
7. **format_final_response:** Aggregates results into structured JSON

**State Management:**
- **ChatState** object tracks entire conversation
- Persistent storage in MongoDB
- In-memory caching for active sessions
- Automatic state recovery on server restart

---

### 6. Dish Enrichment with LLM
**Status:** ✅ Implemented

Automatically enriches dish data using AI when information is missing from menu uploads.

**Auto-Populated Fields:**
- **Ingredients:** Infers typical ingredients for dishes
- **Allergens:** Detects allergens with confidence scores
- **Nutrition Facts:** Estimates calories, protein, fat, carbs, sugar, fiber
- **Serving Size:** Standard portion size estimation

**Confidence Scoring:**
Each auto-populated field includes a confidence score (0.0-1.0):
- `1.0`: Explicit from menu data
- `0.8-0.9`: High confidence inference
- `0.5-0.7`: Moderate confidence
- `<0.5`: Low confidence guess

**Example:**
```json
{
  "dish_name": "Margherita Pizza",
  "explicit_allergens": [
    {
      "allergen": "dairy",
      "confidence": 1.0,
      "why": "Contains mozzarella cheese"
    },
    {
      "allergen": "wheat_gluten",
      "confidence": 0.95,
      "why": "Pizza dough typically contains wheat flour"
    }
  ],
  "nutrition_facts": {
    "calories": {"value": 250, "confidence": 0.85},
    "protein": {"value": 12, "confidence": 0.80},
    "fat": {"value": 9, "confidence": 0.80}
  }
}
```

---

### 7. Response Synthesis
**Status:** ✅ Implemented

Aggregates results from multiple retrievers into a unified, structured response.

**Response Structure:**
```json
{
  "user_id": "user123",
  "session_id": "session456",
  "restaurant_id": "rest789",
  "original_query": "Show me vegan pizzas and calories in margherita",
  "responses": [
    {
      "query": "Show me vegan pizzas",
      "type": "menu_search",
      "result": [
        {
          "dish_name": "Vegan Supreme Pizza",
          "price": 14.99,
          "ingredients": ["tomato sauce", "vegan cheese", "vegetables"],
          "allergens": ["soy"],
          "safe_for_user": true
        }
      ]
    },
    {
      "query": "calories in margherita",
      "type": "dish_info",
      "result": {
        "dish_name": "Margherita Pizza",
        "nutrition_facts": {
          "calories": 250,
          "protein": 12,
          "fat": 9
        }
      }
    }
  ],
  "status": "success",
  "timestamp": "2025-12-01T10:30:00Z"
}
```

---

## User Management Features

### 8. User Authentication
**Status:** ✅ Implemented

Secure user account management with JWT-based authentication.

**Features:**
- User registration (signup)
- Password hashing with bcrypt
- JWT token generation on login
- Token-based session management
- Protected route authentication

**Endpoints:**
```
POST   /users/signup     - Create new account
POST   /users/login      - Authenticate (returns Bearer token)
GET    /users/me         - Get current user (requires auth)
PUT    /users/me         - Update profile (requires auth)
DELETE /users/me         - Delete account (requires auth)
```

**Security:**
- Passwords hashed using bcrypt (12 rounds)
- JWT tokens for stateless authentication
- Username uniqueness validation
- Secure password requirements

---

### 9. Allergen Preference Management
**Status:** ✅ Implemented

Users can store and manage their allergen preferences for personalized safety filtering.

**Supported Allergens:**
- Peanuts
- Tree nuts
- Dairy
- Eggs
- Soy
- Wheat/Gluten
- Fish
- Shellfish
- Sesame

**Features:**
- Set allergens during signup
- Update allergen list in settings
- Automatic dish filtering based on preferences
- `safe_for_user` flag on all dish results
- Allergen confidence scoring

**User Preference Storage:**
```json
{
  "username": "john_doe",
  "allergen_preferences": ["peanuts", "dairy", "shellfish"]
}
```

**Safety Filtering:**
All dish responses include a `safe_for_user` boolean:
```json
{
  "dish_name": "Thai Peanut Noodles",
  "allergens": ["peanuts", "soy"],
  "safe_for_user": false  // User allergic to peanuts
}
```

---

### 10. User Profile Management
**Status:** ✅ Implemented

Full CRUD operations for user accounts.

**Capabilities:**
- View profile information
- Update name, username, password
- Modify allergen preferences
- Account deletion with data cleanup
- Lookup users by ID or username

---

## Restaurant & Menu Management

### 11. Restaurant CRUD Operations
**Status:** ✅ Implemented

Complete restaurant management system with metadata and menu support.

**Restaurant Data:**
- Name
- Location (address/city)
- Cuisine types (array: Italian, Mexican, etc.)
- Rating (0.0 - 5.0 scale)
- Creation timestamp

**Endpoints:**
```
POST   /restaurants/          - Create restaurant
GET    /restaurants/          - List all restaurants
GET    /restaurants/{id}      - Get single restaurant
PATCH  /restaurants/{id}      - Update restaurant
DELETE /restaurants/{id}      - Delete restaurant
```

---

### 12. Menu CSV Upload
**Status:** ✅ Implemented

Bulk menu import via CSV file upload with automatic processing.

**CSV Format:**
```csv
dish_name,description,price,ingredients,allergens,nutrition_facts
Margherita Pizza,Classic tomato and cheese,12.99,"tomato,cheese,basil","dairy,gluten","{calories:250}"
```

**Processing Pipeline:**
1. CSV file uploaded with restaurant creation
2. Background processing parses CSV
3. Missing fields enriched using LLM
4. Dishes created in database
5. FAISS index updated with new embeddings

**Features:**
- Async processing for large menus
- Automatic ingredient parsing
- Allergen detection
- Nutrition fact extraction
- Error handling and validation

---

### 13. Dish CRUD Operations
**Status:** ✅ Implemented

Individual dish management with rich metadata support.

**Dish Data Model:**
```json
{
  "dish_name": "Caesar Salad",
  "description": "Fresh romaine with caesar dressing",
  "price": 8.99,
  "ingredients": ["romaine lettuce", "parmesan", "croutons", "caesar dressing"],
  "explicit_allergens": [
    {
      "allergen": "dairy",
      "confidence": 1.0,
      "why": "Contains parmesan cheese"
    }
  ],
  "nutrition_facts": {
    "calories": {"value": 180, "confidence": 0.9},
    "protein": {"value": 8, "confidence": 0.85},
    "fat": {"value": 12, "confidence": 0.85},
    "carbohydrates": {"value": 10, "confidence": 0.8}
  },
  "serving_size": "1 bowl",
  "availability": true,
  "restaurant_id": "rest123"
}
```

**Endpoints:**
```
POST   /dishes/{restaurant_id}  - Create dish
GET    /dishes/                 - List all dishes (with filters)
GET    /dishes/filter           - Filter by allergens & restaurant
GET    /dishes/{dish_id}        - Get single dish
PUT    /dishes/{dish_id}        - Update dish
DELETE /dishes/{dish_id}        - Delete dish
```

---

### 14. Advanced Filtering System
**Status:** ✅ Implemented

Multi-dimensional filtering for precise dish discovery.

**Filter Types:**

#### Price Filter
```json
{
  "min_price": 5.00,
  "max_price": 20.00
}
```

#### Ingredient Filter
```json
{
  "include": ["chicken", "vegetables"],
  "exclude": ["seafood", "pork"]
}
```

#### Allergen Filter
```json
{
  "must_be_free_of": ["peanuts", "dairy", "shellfish"]
}
```

#### Nutrition Filter
```json
{
  "max_calories": 500,
  "min_protein": 20,
  "max_fat": 15,
  "max_carbs": 50
}
```

**Filter Application:**
Filters are extracted from natural language queries and applied automatically:
```
"Show me chicken dishes under $15 without dairy"
→ Price filter: max_price = 15
→ Ingredient filter: include = ["chicken"]
→ Allergen filter: must_be_free_of = ["dairy"]
```

---

## Search & Discovery

### 15. Conversational Search Interface
**Status:** ✅ Implemented (Frontend)

Real-time chat interface for menu exploration.

**Features:**
- Message history display
- Auto-scrolling to latest message
- Typing indicators
- Example query suggestions
- Error handling with user-friendly messages
- Session persistence

**UI Components:**
- Query input with submit button
- Scrollable chat history
- Dish result cards with:
  - Dish name and description
  - Price
  - Ingredients list
  - Allergen warnings
  - Nutrition facts
  - Safety indicator (safe_for_user)

---

### 16. Chat History & Session Management
**Status:** ✅ Implemented

Persistent conversation storage with session-based retrieval.

**Features:**
- Unique session ID per user-restaurant pair
- All chat states saved to MongoDB
- Context rebuilding from chat history
- Retrieve full conversation history
- Timestamp tracking

**Endpoints:**
```
GET /restaurants/history/{user_id}/{restaurant_id}
→ Returns all chat states for the session
```

**Data Persistence:**
- Each query and response saved as ChatState
- States include full context, intents, results
- History used for context resolution
- Supports audit trails and analytics

---

## Safety & Allergen Features

### 17. Allergen Detection System
**Status:** ✅ Implemented

Multi-layered allergen detection with confidence scoring.

**Detection Methods:**

#### Explicit Allergens
Directly specified in menu data or CSV upload.
```json
{
  "allergen": "peanuts",
  "confidence": 1.0,
  "why": "Explicitly listed in menu"
}
```

#### Inferred Allergens
AI-detected based on ingredients and dish descriptions.
```json
{
  "allergen": "dairy",
  "confidence": 0.9,
  "why": "Contains cream sauce"
}
```

**Allergen Categories:**
- Peanuts
- Tree nuts (almonds, cashews, walnuts, etc.)
- Dairy (milk, cheese, yogurt, cream, butter)
- Eggs
- Soy
- Wheat/Gluten
- Fish
- Shellfish (shrimp, crab, lobster)
- Sesame

---

### 18. User Safety Filtering
**Status:** ✅ Implemented

Automatic filtering based on user allergen preferences.

**How It Works:**
1. User sets allergen preferences in profile
2. All dish queries check against user preferences
3. Dishes with matching allergens flagged as unsafe
4. `safe_for_user` boolean added to every dish result
5. Frontend displays warning indicators

**Example:**
```
User allergens: ["peanuts", "shellfish"]

Query: "Show me all appetizers"
→ Thai Peanut Spring Rolls (safe_for_user: false) ⚠️
→ Shrimp Cocktail (safe_for_user: false) ⚠️
→ Bruschetta (safe_for_user: true) ✓
```

---

### 19. Nutrition Fact Tracking
**Status:** ✅ Implemented

Comprehensive nutrition information with confidence scoring.

**Tracked Metrics:**
- Calories (kcal)
- Protein (g)
- Fat (g)
- Carbohydrates (g)
- Sugar (g)
- Fiber (g)

**Data Sources:**
- Explicit from menu data
- LLM-inferred estimates
- Standard nutritional databases

**Confidence Levels:**
- **1.0:** Exact from menu
- **0.8-0.9:** High confidence estimate
- **0.5-0.7:** Moderate estimate
- **<0.5:** Low confidence guess

**Usage in Queries:**
```
"Show me dishes under 400 calories"
"List high protein options"
"Find low carb meals"
```

---

## API Features

### 20. RESTful API Architecture
**Status:** ✅ Implemented

FastAPI-based REST API with OpenAPI documentation.

**Features:**
- Auto-generated API docs at `/docs`
- Swagger UI at `/docs`
- ReDoc UI at `/redoc`
- JSON request/response format
- Pydantic validation
- Error handling with structured responses

**Base URL:**
- Development: `http://localhost:8000`
- Production: `https://safebites-yu1o.onrender.com`

---

### 21. CORS Configuration
**Status:** ✅ Implemented

Cross-Origin Resource Sharing for frontend communication.

**Allowed Origins:**
- `http://localhost:8080`
- `http://localhost:8000`
- `http://localhost:5173`
- `https://se-wolfcafe.vercel.app`

**Allowed Methods:**
- GET, POST, PUT, PATCH, DELETE, OPTIONS

**Allowed Headers:**
- Content-Type, Authorization

---

### 22. Error Handling
**Status:** ✅ Implemented

Comprehensive error handling with custom exceptions.

**Exception Types:**
- `BadRequestException` (400)
- `NotFoundException` (404)
- `UnauthorizedException` (401)
- `GenericException` (500)

**Error Response Format:**
```json
{
  "detail": "User not found",
  "status_code": 404,
  "error_type": "NotFoundException"
}
```

---

## Frontend Features

### 23. React Single Page Application
**Status:** ✅ Implemented

Modern React app with TypeScript and Tailwind CSS.

**Technology Stack:**
- React 19.1.1
- TypeScript
- React Router DOM 7.9.4
- Tailwind CSS
- Vite 7.1.7

**Pages:**
1. **Welcome** - Landing page with project overview
2. **SignUp** - User registration form
3. **Login** - Authentication page
4. **Dashboard** - Main navigation hub
5. **Home** - Restaurant listing with filters
6. **SearchChat** - AI-powered chat interface
7. **RestaurantMenu** - Browse specific restaurant menu
8. **DishDetail** - Detailed dish view
9. **AddRestaurant** - Restaurant creation form
10. **Settings** - User profile and preferences

---

### 24. Responsive Design
**Status:** ✅ Implemented

Mobile-first responsive design with Tailwind CSS.

**Features:**
- Adaptive layouts for mobile, tablet, desktop
- Touch-friendly interfaces
- Optimized font sizes
- Responsive images
- Mobile navigation

---

### 25. State Management
**Status:** ✅ Implemented

Client-side state management using React hooks and localStorage.

**Stored Data:**
- Authentication token (Bearer)
- User profile data
- Active session ID
- Restaurant context

**State Persistence:**
- LocalStorage for auth tokens
- Session storage for temporary data
- React state for UI updates

---

### 26. Frontend Testing
**Status:** ✅ Implemented

Comprehensive test suite with Vitest and React Testing Library.

**Test Coverage:**
- Component rendering tests
- User interaction tests
- Form validation tests
- API integration tests
- Error handling tests

**Test Files:**
- `Home.test.tsx`
- `Login.test.tsx`
- `SignUp.test.tsx`
- `Dashboard.test.tsx`
- `SearchChat.test.tsx`
- `Settings.test.tsx`
- `AddRestaurant.test.tsx`
- `Welcome.test.tsx`

**Running Tests:**
```bash
npm run test              # Run all tests
npm run test -- --watch   # Watch mode
npm run test:ui           # UI test interface
```

---

## Backend Features

### 27. Comprehensive Logging
**Status:** ✅ Implemented

Multi-level logging system with rotating file handlers.

**Log Outputs:**
1. **Console:** INFO level with colored formatting
2. **Debug File:** DEBUG level (`logs/debug.log`)
3. **Error File:** ERROR level (`logs/error.log`)

**Log Format:**
```
2025-12-01 10:30:45 | INFO | app.services.context_resolver | context_resolver.py:42 | Resolving context for query: "show me pizzas"
```

**Features:**
- Rotating file handlers (5MB per file, 5 backups)
- Separate error log file
- Colored console output
- Timestamp tracking
- Module and line number tracking

---

### 28. Backend Testing
**Status:** ✅ Implemented

Pytest-based test suite with fixtures and coverage reporting.

**Test Types:**
- Unit tests (individual functions)
- Integration tests (full workflows)

**Test Markers:**
```python
@pytest.mark.unit
@pytest.mark.integration
```

**Running Tests:**
```bash
pytest                    # All tests
pytest --cov=app         # With coverage
pytest -m unit           # Unit tests only
pytest -m integration    # Integration tests only
```

**Fixtures:**
- `db_client`: MongoDB test client
- `client`: FastAPI TestClient
- Automatic database cleanup

---

### 29. Background Processing
**Status:** ✅ Implemented

Async background tasks for heavy operations.

**Use Cases:**
- Menu CSV processing
- FAISS index updates
- Dish enrichment with LLM
- Bulk operations

**Benefits:**
- Non-blocking API responses
- Scalable for large datasets
- Retry logic on failures

---

### 30. Database Indexing
**Status:** ✅ Implemented

MongoDB indexes for query optimization.

**Indexed Fields:**
- `users.username` (unique)
- `restaurants._id`
- `dishes.restaurant_id`
- `dishes.dish_name`
- `sessions.session_id`
- `chat_states.session_id`

**Performance Impact:**
- Faster user lookups
- Optimized dish queries
- Efficient session retrieval

---

## Future Roadmap

### Planned for Project 3

#### 31. Personalized Dish Recommender
**Status:** 🔄 Planned

ML-based recommendation system using user embeddings.

**Planned Features:**
- User preference learning
- Collaborative filtering
- Content-based recommendations
- Hybrid recommendation model
- Personalized dish rankings

---

#### 32. Chat-based Ordering
**Status:** 🔄 Planned

Conversational order placement through chat interface.

**Planned Features:**
- Add to cart via chat
- Order customization ("no onions", "extra cheese")
- Order summary and confirmation
- Payment integration
- Order tracking

---

#### 33. Delivery Tracking Dashboard
**Status:** 🔄 Planned

Real-time order tracking with live updates.

**Planned Features:**
- Live order status updates
- Driver location tracking
- ETA calculations
- Push notifications
- Order history

---

#### 34. Admin Analytics Dashboard
**Status:** 🔄 Planned

Restaurant owner analytics and insights.

**Planned Features:**
- Sales analytics
- Popular dishes tracking
- User engagement metrics
- Query analytics
- Revenue reports
- Export functionality

---

## Feature Summary Table

| Feature | Status | Backend | Frontend | AI/ML |
|---------|--------|---------|----------|-------|
| User Authentication | ✅ | ✓ | ✓ | |
| Allergen Management | ✅ | ✓ | ✓ | |
| Restaurant CRUD | ✅ | ✓ | ✓ | |
| Dish Management | ✅ | ✓ | ✓ | |
| Menu CSV Upload | ✅ | ✓ | ✓ | |
| Semantic Search | ✅ | ✓ | ✓ | ✓ |
| Intent Classification | ✅ | ✓ | | ✓ |
| Context Resolution | ✅ | ✓ | | ✓ |
| LangGraph Pipeline | ✅ | ✓ | | ✓ |
| Chat Interface | ✅ | ✓ | ✓ | |
| Chat History | ✅ | ✓ | ✓ | |
| Dish Enrichment | ✅ | ✓ | | ✓ |
| Safety Filtering | ✅ | ✓ | ✓ | |
| Nutrition Tracking | ✅ | ✓ | ✓ | |
| Advanced Filtering | ✅ | ✓ | ✓ | |
| Response Synthesis | ✅ | ✓ | | ✓ |
| Logging System | ✅ | ✓ | | |
| Testing Suite | ✅ | ✓ | ✓ | |
| API Documentation | ✅ | ✓ | | |
| Personalized Recommender | 🔄 | | | |
| Chat-based Ordering | 🔄 | | | |
| Delivery Tracking | 🔄 | | | |
| Admin Analytics | 🔄 | | | |

**Legend:**
- ✅ Implemented
- 🔄 Planned
- ✓ Component includes this feature

---

## Technical Statistics

**Backend:**
- **Total Services:** 12
- **API Endpoints:** 20+
- **Database Collections:** 5
- **LangGraph Nodes:** 7
- **Supported Allergens:** 9
- **Intent Types:** 4

**Frontend:**
- **Pages:** 10
- **Test Files:** 8
- **Components:** 15+

**AI/ML:**
- **LLM Models Used:** GPT-4o-mini
- **Embedding Dimensions:** 1536
- **Vector Database:** FAISS (CPU)
- **Processing Pipeline Nodes:** 7

---

## Contact & Support

For feature requests, bug reports, or contributions, please refer to:
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
- GitHub Issues

---

**Last Updated:** December 2025
**Version:** Project 2 - Production Release
