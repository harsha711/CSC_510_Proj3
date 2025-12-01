# Getting Started with SafeBites

Welcome to SafeBites! This comprehensive guide will walk you through setting up the development environment, understanding the architecture, and making your first contributions to the project.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Initial Setup](#initial-setup)
3. [Backend Setup](#backend-setup)
4. [Frontend Setup](#frontend-setup)
5. [Database Configuration](#database-configuration)
6. [Running the Application](#running-the-application)
7. [Understanding the Architecture](#understanding-the-architecture)
8. [Making Your First Changes](#making-your-first-changes)
9. [Testing](#testing)
10. [Troubleshooting](#troubleshooting)
11. [Next Steps](#next-steps)

---

## Prerequisites

Before you begin, ensure you have the following installed on your system:

### Required Software

#### 1. Python 3.10 or Higher
```bash
# Check Python version
python --version
# or
python3 --version

# Should output: Python 3.10.x or higher
```

**Installation:**
- **Windows:** Download from [python.org](https://www.python.org/downloads/)
- **Mac:** `brew install python@3.10`
- **Linux:** `sudo apt-get install python3.10`

#### 2. Node.js 18+ and npm
```bash
# Check Node.js version
node --version
# Should output: v18.x.x or higher

# Check npm version
npm --version
# Should output: 9.x.x or higher
```

**Installation:**
- Download from [nodejs.org](https://nodejs.org/)
- Or use nvm (Node Version Manager):
  ```bash
  nvm install 18
  nvm use 18
  ```

#### 3. MongoDB
You can use either:
- **Local MongoDB installation**
- **MongoDB Atlas (cloud)**

**Local Installation:**
- **Windows/Mac:** Download from [mongodb.com/try/download/community](https://www.mongodb.com/try/download/community)
- **Linux:** `sudo apt-get install mongodb`

**Cloud Setup (MongoDB Atlas):**
1. Create free account at [cloud.mongodb.com](https://cloud.mongodb.com)
2. Create a cluster (free tier available)
3. Get your connection string

#### 4. Git
```bash
# Check Git version
git --version
```

**Installation:**
- Download from [git-scm.com](https://git-scm.com/)

#### 5. OpenAI API Key
1. Sign up at [platform.openai.com](https://platform.openai.com)
2. Create an API key
3. Add credits to your account (required for API usage)

### Recommended Tools

- **VS Code** or **PyCharm** (IDE)
- **Postman** or **Insomnia** (API testing)
- **MongoDB Compass** (database GUI)
- **Git GUI Client** (optional: GitKraken, SourceTree)

---

## Initial Setup

### 1. Clone the Repository

```bash
# Clone the repository
git clone https://github.com/yourusername/CSC_510_Proj3.git

# Navigate to the project directory
cd CSC_510_Proj3

# Navigate to the SafeBites project
cd proj2/SafeBites
```

### 2. Verify Directory Structure

```bash
# List directory contents
ls -la

# You should see:
# - backend/
# - frontend/
# - docs/
```

---

## Backend Setup

### Step 1: Navigate to Backend Directory

```bash
cd backend
```

### Step 2: Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` prefix in your terminal prompt.

### Step 3: Install Python Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install all dependencies
pip install -r requirements.txt
```

This will install:
- FastAPI and uvicorn
- LangChain and LangGraph
- MongoDB driver (pymongo)
- OpenAI SDK
- FAISS for vector search
- Testing libraries (pytest)
- And other dependencies

**Expected installation time:** 2-5 minutes

### Step 4: Create Environment File

Create a `.env` file in the `backend/` directory:

```bash
# Windows (PowerShell)
New-Item .env -ItemType File

# Mac/Linux
touch .env
```

Add the following content to `.env`:

```env
# MongoDB Configuration
MONGO_URI=mongodb://localhost:27017
DB_NAME=foodapp
TEST_DB_NAME=foodapp_test

# OpenAI Configuration
OPENAI_API_KEY=sk-your-actual-openai-api-key-here

# JWT Configuration (optional - will use default if not set)
JWT_SECRET=your-secret-key-for-jwt-tokens

# Logging Configuration (optional)
LOG_LEVEL=INFO
```

**Important:** Replace `sk-your-actual-openai-api-key-here` with your real OpenAI API key.

### Step 5: Verify Backend Setup

```bash
# Check if all imports work
python -c "import fastapi, langchain, pymongo, openai, faiss; print('All imports successful!')"
```

If no errors appear, your backend is set up correctly!

---

## Frontend Setup

### Step 1: Navigate to Frontend Directory

```bash
# From the SafeBites root directory
cd frontend
```

### Step 2: Install Node Dependencies

```bash
# Install all dependencies
npm install
```

This will install:
- React 19.1.1
- TypeScript
- Vite
- React Router
- Tailwind CSS
- Testing libraries (Vitest)
- And other dependencies

**Expected installation time:** 1-3 minutes

### Step 3: Create Environment File

Create a `.env.local` file in the `frontend/` directory:

```bash
# Windows (PowerShell)
New-Item .env.local -ItemType File

# Mac/Linux
touch .env.local
```

Add the following content:

```env
VITE_API_BASE_URL=http://localhost:8000
```

### Step 4: Verify Frontend Setup

```bash
# Check if build works
npm run build

# Should complete without errors
```

---

## Database Configuration

### Option 1: Local MongoDB

#### Start MongoDB Service

**Windows:**
```bash
# Start MongoDB service
net start MongoDB

# Or run manually
mongod --dbpath C:\data\db
```

**Mac:**
```bash
# Start with Homebrew
brew services start mongodb-community

# Or run manually
mongod --config /usr/local/etc/mongod.conf
```

**Linux:**
```bash
# Start service
sudo systemctl start mongod

# Enable on startup
sudo systemctl enable mongod
```

#### Verify MongoDB is Running

```bash
# Connect to MongoDB shell
mongosh

# Or older MongoDB versions
mongo

# You should see MongoDB shell prompt
```

#### Create Database

```javascript
// In MongoDB shell
use foodapp

// Create a test collection
db.test.insertOne({message: "Hello SafeBites"})

// Verify
db.test.find()

// Exit
exit
```

### Option 2: MongoDB Atlas (Cloud)

#### Setup Steps

1. **Create Cluster**
   - Go to [cloud.mongodb.com](https://cloud.mongodb.com)
   - Click "Build a Database"
   - Select "Free Shared" tier
   - Choose a cloud provider and region
   - Click "Create Cluster"

2. **Create Database User**
   - Go to "Database Access"
   - Click "Add New Database User"
   - Choose "Password" authentication
   - Set username and password (save these!)
   - Grant "Read and write to any database" role

3. **Configure Network Access**
   - Go to "Network Access"
   - Click "Add IP Address"
   - Select "Allow Access from Anywhere" (0.0.0.0/0)
   - Or add your specific IP address

4. **Get Connection String**
   - Go to "Database" → "Connect"
   - Choose "Connect your application"
   - Copy the connection string
   - Format: `mongodb+srv://username:password@cluster.xxxxx.mongodb.net/`

5. **Update Backend .env**
   ```env
   MONGO_URI=mongodb+srv://username:password@cluster.xxxxx.mongodb.net/
   DB_NAME=foodapp
   ```

---

## Running the Application

### Start Backend Server

```bash
# Navigate to backend directory
cd proj2/SafeBites/backend

# Activate virtual environment (if not already active)
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Start the server
uvicorn app.main:app --reload
```

**Expected output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Access Points:**
- API: `http://localhost:8000`
- Interactive API docs: `http://localhost:8000/docs`
- Alternative docs: `http://localhost:8000/redoc`
- Health check: `http://localhost:8000/`

### Start Frontend Development Server

Open a **new terminal window** (keep backend running):

```bash
# Navigate to frontend directory
cd proj2/SafeBites/frontend

# Start development server
npm run dev
```

**Expected output:**
```
  VITE v7.1.7  ready in 500 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

**Access:**
- Open browser to `http://localhost:5173`

### Verify Everything Works

1. **Check Backend Health**
   - Visit `http://localhost:8000` in browser
   - Should see: `{"message": "Welcome to SafeBites API"}`

2. **Check API Documentation**
   - Visit `http://localhost:8000/docs`
   - Should see interactive Swagger UI

3. **Check Frontend**
   - Visit `http://localhost:5173`
   - Should see SafeBites welcome page

4. **Test End-to-End**
   - Click "Sign Up" on frontend
   - Create an account
   - Login
   - Browse restaurants

---

## Understanding the Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────┐
│                   USER BROWSER                  │
│           (React Frontend @ :5173)              │
└─────────────────────┬───────────────────────────┘
                      │ HTTP Requests
                      ▼
┌─────────────────────────────────────────────────┐
│              FastAPI Backend @ :8000             │
│  ┌──────────────────────────────────────────┐   │
│  │         API Routes (Routers)             │   │
│  │  /users  /restaurants  /dishes           │   │
│  └──────────────┬───────────────────────────┘   │
│                 ▼                                │
│  ┌──────────────────────────────────────────┐   │
│  │        Business Logic (Services)         │   │
│  │  - User Service                          │   │
│  │  - Restaurant Service                    │   │
│  │  - Intent Service                        │   │
│  │  - FAISS Service (semantic search)       │   │
│  └──────────────┬───────────────────────────┘   │
│                 ▼                                │
│  ┌──────────────────────────────────────────┐   │
│  │     LangGraph Conversation Pipeline      │   │
│  │  Context → Intent → Retrieve → Respond   │   │
│  └──────────────┬───────────────────────────┘   │
└─────────────────┼────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────┐
│         MongoDB Database                        │
│  Collections: users, restaurants, dishes,       │
│              sessions, chat_states              │
└─────────────────────────────────────────────────┘
                  +
┌─────────────────────────────────────────────────┐
│         OpenAI API                              │
│  - GPT-4o-mini (intent, context)                │
│  - text-embedding-3-large (embeddings)          │
└─────────────────────────────────────────────────┘
                  +
┌─────────────────────────────────────────────────┐
│         FAISS Vector Index                      │
│  - In-memory semantic search                    │
│  - 1536-dimensional embeddings                  │
└─────────────────────────────────────────────────┘
```

### Backend Architecture

#### Directory Structure Deep Dive

```
backend/app/
│
├── main.py                    # FastAPI application entry point
│   - Initializes FastAPI app
│   - Configures CORS middleware
│   - Registers routers
│   - Startup events (FAISS index)
│
├── config.py                  # Configuration management
│   - Environment variables
│   - Logging setup (console + file)
│   - MongoDB connection settings
│
├── db.py                      # Database connection
│   - MongoClient initialization
│   - get_db() function
│
├── models/                    # Pydantic data models
│   ├── user_model.py          # User schemas (Create, Update, Out)
│   ├── dish_model.py          # Dish schemas with allergen info
│   ├── restaurant_model.py    # Restaurant schemas
│   ├── intent_model.py        # Intent extraction schemas
│   └── responder_model.py     # Response format schemas
│
├── routers/                   # API endpoints
│   ├── user_router.py         # /users/* endpoints
│   ├── restaurant_router.py   # /restaurants/* endpoints
│   └── dish_router.py         # /dishes/* endpoints
│
├── services/                  # Business logic layer
│   ├── user_service.py        # User CRUD operations
│   ├── restaurant_service.py  # Restaurant + menu management
│   ├── dish_service.py        # Dish operations
│   ├── intent_service.py      # Intent extraction using LLM
│   ├── context_resolver.py    # Query rewriting + context
│   ├── faiss_service.py       # Semantic search with FAISS
│   ├── retrieval_service.py   # Menu item retrieval
│   ├── dish_info_service.py   # Dish information retrieval
│   └── response_synthesizer_tool.py  # Response formatting
│
├── flow/                      # LangGraph conversation pipeline
│   ├── state.py               # ChatState model
│   ├── graph.py               # Pipeline node definitions
│   └── state_store.py         # In-memory state storage
│
├── utils/                     # Helper utilities
│   ├── faiss_index.py         # FAISS index management
│   └── llm_tracker.py         # LLM usage tracking
│
├── tests/                     # Test suite
│   ├── unit/                  # Unit tests
│   └── integration/           # Integration tests
│
└── logs/                      # Application logs
    ├── debug.log              # All logs
    └── error.log              # Error-only logs
```

#### Request Flow Example

Let's trace a user query: **"Show me vegan pizzas under $15"**

```
1. Frontend sends POST to /restaurants/search
   Body: {
     "query": "Show me vegan pizzas under $15",
     "user_id": "user123",
     "restaurant_id": "rest456"
   }

2. Router (restaurant_router.py) receives request
   → Calls graph.invoke(state) to start pipeline

3. LangGraph Pipeline Execution:

   a) Context Resolver (context_resolver.py)
      - Checks if query has references ("that pizza", "it")
      - None found, query unchanged
      - Context: empty (first message)

   b) Intent Classifier (intent_service.py)
      - Sends to GPT-4o-mini: "Extract intents from: Show me vegan pizzas under $15"
      - Returns: {"intents": [{"type": "menu_search", "query": "vegan pizzas under $15"}]}

   c) Query Part Generator
      - Organizes intents: menu_search_queries = ["vegan pizzas under $15"]

   d) Menu Retriever (retrieval_service.py)
      - Calls FAISS service with query
      - FAISS Service (faiss_service.py):
        * Embeds query: "vegan pizzas under $15" → [1536 dims]
        * Searches vector index for similar dishes
        * Returns top 10 matches
      - Applies filters:
        * Price filter: price <= 15
        * Ingredient filter: include "vegan" ingredients
      - Returns 5 matching pizzas

   e) Response Synthesizer (response_synthesizer_tool.py)
      - Formats results as JSON:
        {
          "responses": [{
            "query": "vegan pizzas under $15",
            "type": "menu_search",
            "result": [
              {
                "dish_name": "Vegan Margherita",
                "price": 12.99,
                "ingredients": ["tomato", "vegan cheese", "basil"],
                "safe_for_user": true
              },
              ...
            ]
          }],
          "status": "success"
        }

4. Router returns JSON response to frontend

5. Frontend displays results in chat interface
```

### Frontend Architecture

#### Directory Structure

```
frontend/src/
│
├── main.tsx                   # React entry point
│   - Renders <App /> into DOM
│
├── App.tsx                    # Root component
│   - React Router setup
│   - Route definitions
│
├── App.css                    # Global styles
│
├── pages/                     # Page components
│   ├── Welcome.tsx            # Landing page
│   ├── SignUp.tsx             # User registration
│   ├── Login.tsx              # Authentication
│   ├── Dashboard.tsx          # Main hub
│   ├── Home.tsx               # Restaurant listing
│   ├── SearchChat.tsx         # AI chat interface
│   ├── RestaurantMenu.tsx     # Menu browsing
│   ├── DishDetail.tsx         # Dish details
│   ├── AddRestaurant.tsx      # Restaurant creation
│   └── Settings.tsx           # User settings
│
├── frontend_test/             # Test files
│   ├── Home.test.tsx
│   ├── Login.test.tsx
│   └── ...
│
└── assets/                    # Static assets (images, etc.)
```

### LangGraph Pipeline Detailed

The conversation pipeline is the heart of SafeBites' AI capabilities:

```python
# From backend/app/flow/graph.py

from langgraph.graph import StateGraph

# Create state machine
graph = StateGraph(ChatState)

# Add nodes (processing steps)
graph.add_node("context_resolver", resolve_context)
graph.add_node("intent_classifier", classify_intent)
graph.add_node("query_part_generator", generate_query_parts)
graph.add_node("menu_retriever", retrieve_menu_items)
graph.add_node("informative_retriever", retrieve_dish_info)
graph.add_node("format_final_response", synthesize_response)

# Define edges (flow)
graph.add_edge("context_resolver", "intent_classifier")
graph.add_edge("intent_classifier", "query_part_generator")
graph.add_edge("query_part_generator", "menu_retriever")
graph.add_edge("query_part_generator", "informative_retriever")
graph.add_edge("menu_retriever", "format_final_response")
graph.add_edge("informative_retriever", "format_final_response")

# Set entry point
graph.set_entry_point("context_resolver")

# Compile graph
app = graph.compile()
```

---

## Making Your First Changes

### Example 1: Add a New API Endpoint

Let's add a simple health check endpoint for dishes.

#### Step 1: Edit Router

File: `backend/app/routers/dish_router.py`

```python
# Add this endpoint
@router.get("/health")
def dish_health_check():
    """Health check for dish service"""
    return {
        "status": "healthy",
        "service": "dish_service",
        "timestamp": datetime.utcnow().isoformat()
    }
```

#### Step 2: Test Endpoint

```bash
# Restart backend server (Ctrl+C, then re-run)
uvicorn app.main:app --reload

# Test endpoint
curl http://localhost:8000/dishes/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "dish_service",
  "timestamp": "2025-12-01T10:30:00.000Z"
}
```

### Example 2: Add a Frontend Component

Let's add a simple footer component.

#### Step 1: Create Component

File: `frontend/src/components/Footer.tsx`

```typescript
export function Footer() {
  return (
    <footer className="bg-gray-800 text-white py-4 mt-auto">
      <div className="container mx-auto text-center">
        <p>© 2025 SafeBites - AI-Powered Food Discovery</p>
      </div>
    </footer>
  );
}
```

#### Step 2: Use Component

File: `frontend/src/App.tsx`

```typescript
import { Footer } from './components/Footer';

function App() {
  return (
    <div className="min-h-screen flex flex-col">
      {/* Existing routes */}
      <Routes>
        {/* ... */}
      </Routes>

      <Footer />
    </div>
  );
}
```

#### Step 3: View Changes

Frontend automatically reloads - check `http://localhost:5173`

---

## Testing

### Backend Testing

#### Run All Tests

```bash
cd backend

# Activate virtual environment
source venv/bin/activate  # Mac/Linux
# or
venv\Scripts\activate  # Windows

# Run tests
pytest

# With verbose output
pytest -v

# With coverage
pytest --cov=app --cov-report=html
```

#### Run Specific Tests

```bash
# Unit tests only
pytest -m unit

# Integration tests only
pytest -m integration

# Specific test file
pytest tests/unit/test_intent_service.py

# Specific test function
pytest tests/unit/test_intent_service.py::test_extract_menu_search_intent
```

#### Write a Test

File: `backend/app/tests/unit/test_dish_service.py`

```python
import pytest
from app.services.dish_service import get_dish_by_id

def test_get_dish_by_id():
    """Test retrieving dish by ID"""
    # This is a placeholder - implement with actual logic
    dish_id = "test_dish_123"
    result = get_dish_by_id(dish_id)

    assert result is not None
    assert result["_id"] == dish_id
```

### Frontend Testing

#### Run All Tests

```bash
cd frontend

# Run tests
npm run test

# Watch mode (re-runs on file changes)
npm run test -- --watch

# UI test interface
npm run test:ui

# Coverage report
npm run test -- --coverage
```

#### Write a Test

File: `frontend/src/frontend_test/Footer.test.tsx`

```typescript
import { render, screen } from '@testing-library/react';
import { Footer } from '../components/Footer';

test('renders footer with copyright', () => {
  render(<Footer />);
  const copyrightText = screen.getByText(/© 2025 SafeBites/i);
  expect(copyrightText).toBeInTheDocument();
});
```

---

## Troubleshooting

### Common Issues and Solutions

#### 1. Backend Won't Start

**Error:** `ModuleNotFoundError: No module named 'fastapi'`

**Solution:**
```bash
# Make sure virtual environment is activated
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

---

**Error:** `Could not connect to MongoDB`

**Solution:**
```bash
# Check MongoDB is running
# Mac:
brew services list | grep mongodb

# Windows:
sc query MongoDB

# Linux:
sudo systemctl status mongod

# If not running, start it:
# Mac:
brew services start mongodb-community

# Windows:
net start MongoDB

# Linux:
sudo systemctl start mongod
```

---

**Error:** `OpenAI API key not found`

**Solution:**
```bash
# Check .env file exists
ls -la backend/.env

# Verify OPENAI_API_KEY is set
cat backend/.env | grep OPENAI_API_KEY

# Make sure no spaces around = sign:
# ✓ OPENAI_API_KEY=sk-...
# ✗ OPENAI_API_KEY = sk-...
```

---

#### 2. Frontend Won't Start

**Error:** `Cannot find module 'react'`

**Solution:**
```bash
# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

---

**Error:** `VITE_API_BASE_URL is not defined`

**Solution:**
```bash
# Check .env.local exists
ls -la frontend/.env.local

# Create if missing
echo "VITE_API_BASE_URL=http://localhost:8000" > .env.local

# Restart dev server
npm run dev
```

---

**Error:** `Network error when calling API`

**Solution:**
```bash
# 1. Check backend is running
curl http://localhost:8000

# 2. Check CORS settings in backend/app/main.py
# Make sure http://localhost:5173 is in allowed origins

# 3. Check frontend .env.local has correct URL
cat .env.local
# Should show: VITE_API_BASE_URL=http://localhost:8000
```

---

#### 3. FAISS Index Errors

**Error:** `FAISS index not found`

**Solution:**
```bash
# Delete and rebuild index
rm -rf backend/faiss_index_restaurant/

# Restart backend - it will rebuild automatically
uvicorn app.main:app --reload
```

---

**Error:** `Embedding dimension mismatch`

**Solution:**
```bash
# This happens when OpenAI embedding model changes
# Delete index and rebuild:
rm -rf backend/faiss_index_restaurant/

# Restart backend
```

---

#### 4. Database Issues

**Error:** `Authentication failed` (MongoDB Atlas)

**Solution:**
1. Check username/password in connection string
2. URL-encode password if it contains special characters:
   ```
   # If password is: P@ssw0rd!
   # Encode as: P%40ssw0rd%21
   ```
3. Verify database user has correct permissions in Atlas dashboard

---

**Error:** `No database named 'foodapp'`

**Solution:**
```bash
# MongoDB creates databases on first write
# Run this to create:
mongosh

# In MongoDB shell:
use foodapp
db.test.insertOne({init: true})
exit
```

---

#### 5. Testing Issues

**Error:** `Test database not found`

**Solution:**
```bash
# Check TEST_DB_NAME in .env
cat backend/.env | grep TEST_DB_NAME

# Should be set to a different name than DB_NAME:
# DB_NAME=foodapp
# TEST_DB_NAME=foodapp_test
```

---

### Getting Help

If you encounter issues not covered here:

1. **Check Logs**
   ```bash
   # Backend logs
   tail -f backend/app/logs/debug.log
   tail -f backend/app/logs/error.log
   ```

2. **Check GitHub Issues**
   - Search existing issues
   - Create new issue with error details

3. **Ask the Team**
   - Post in project Discord/Slack
   - Tag relevant team members

---

## Next Steps

Congratulations! You now have SafeBites running locally. Here's what to explore next:

### 1. Learn the Codebase

#### Week 1: Frontend
- [ ] Study `SearchChat.tsx` - main chat interface
- [ ] Understand React Router setup in `App.tsx`
- [ ] Explore state management patterns
- [ ] Read frontend test files

#### Week 2: Backend API
- [ ] Study router files (user, restaurant, dish)
- [ ] Understand Pydantic models
- [ ] Explore service layer
- [ ] Test API endpoints with Postman

#### Week 3: AI/ML Components
- [ ] Study LangGraph pipeline in `flow/graph.py`
- [ ] Understand `intent_service.py`
- [ ] Explore `context_resolver.py`
- [ ] Learn about FAISS in `faiss_service.py`

#### Week 4: Database & Testing
- [ ] Understand MongoDB schema
- [ ] Study database indexes
- [ ] Write unit tests
- [ ] Write integration tests

### 2. Make Contributions

#### Beginner Tasks
- [ ] Fix typos in documentation
- [ ] Add more test cases
- [ ] Improve error messages
- [ ] Add code comments

#### Intermediate Tasks
- [ ] Add new API endpoint
- [ ] Create new frontend component
- [ ] Improve allergen detection
- [ ] Add new filter type

#### Advanced Tasks
- [ ] Improve LangGraph pipeline
- [ ] Optimize FAISS search
- [ ] Add new intent type
- [ ] Implement caching layer

### 3. Explore Documentation

- [ ] Read [features.md](features.md) for complete feature list
- [ ] Review [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines
- [ ] Check [SELF_ASSESSMENT.md](SELF_ASSESSMENT.md) for project rubric

### 4. Learn Technologies

#### LangChain & LangGraph
- [LangChain Docs](https://python.langchain.com/)
- [LangGraph Tutorial](https://langchain-ai.github.io/langgraph/)

#### FAISS
- [FAISS Wiki](https://github.com/facebookresearch/faiss/wiki)
- [Vector Search Tutorial](https://www.pinecone.io/learn/vector-search/)

#### FastAPI
- [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/)
- [Pydantic Docs](https://docs.pydantic.dev/)

#### React & TypeScript
- [React Docs](https://react.dev/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)

### 5. Development Workflow

#### Daily Workflow
1. Pull latest changes: `git pull origin main`
2. Create feature branch: `git checkout -b feature/your-feature`
3. Make changes and test locally
4. Write tests for new code
5. Commit with clear message: `git commit -m "Add: feature description"`
6. Push branch: `git push origin feature/your-feature`
7. Create Pull Request on GitHub

#### Before Committing
```bash
# Run tests
cd backend && pytest
cd ../frontend && npm run test

# Check code style
# Backend:
black app/  # Format code
flake8 app/  # Lint code

# Frontend:
npm run lint
```

---

## Additional Resources

### Useful Commands Cheat Sheet

#### Backend
```bash
# Start server
uvicorn app.main:app --reload

# Run tests
pytest

# Format code
black app/

# Create migration (if using Alembic)
alembic revision --autogenerate -m "description"
```

#### Frontend
```bash
# Start dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run tests
npm run test

# Lint code
npm run lint
```

#### Database
```bash
# MongoDB shell
mongosh

# Export data
mongoexport --db=foodapp --collection=dishes --out=dishes.json

# Import data
mongoimport --db=foodapp --collection=dishes --file=dishes.json
```

#### Git
```bash
# Create branch
git checkout -b feature/name

# Stage changes
git add .

# Commit
git commit -m "message"

# Push
git push origin feature/name

# Pull latest
git pull origin main
```

---

## Conclusion

You're now ready to develop with SafeBites!

**Key Takeaways:**
- Backend runs on port 8000 (FastAPI + LangGraph)
- Frontend runs on port 5173 (React + Vite)
- MongoDB stores all data
- OpenAI powers the AI features
- FAISS enables semantic search

**Remember:**
- Always activate virtual environment for backend work
- Keep backend and frontend running in separate terminals
- Check logs when debugging
- Write tests for new features
- Follow contribution guidelines

**Happy coding!** 🚀

---

**Questions or Issues?**
- Check [Troubleshooting](#troubleshooting) section
- Review existing GitHub issues
- Ask in project chat/Discord
- Contact team leads

**Last Updated:** December 2025
**Version:** 2.0 (Project 2)
