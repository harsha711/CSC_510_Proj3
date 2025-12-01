# SafeBites - AI-Powered Food Discovery Platform

![SafeBites](https://img.shields.io/badge/version-2.0-blue)
![Python](https://img.shields.io/badge/python-3.10%2B-brightgreen)
![React](https://img.shields.io/badge/react-19.1.1-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-latest-green)
![License](https://img.shields.io/badge/license-MIT-orange)

> An intelligent conversational AI platform for discovering restaurant menus with semantic search, allergen safety, and natural language understanding.

---

## Overview

**SafeBites** is a modern full-stack web application that revolutionizes how users interact with restaurant menus. By combining cutting-edge AI technologies like LangGraph, LangChain, and FAISS vector search with a responsive React frontend, SafeBites enables users to discover food through natural conversations while ensuring allergen safety.

### Key Highlights

- **🤖 Conversational AI:** Chat naturally to find dishes ("Show me spicy vegan options under $15")
- **🔍 Semantic Search:** FAISS-powered vector search understands meaning, not just keywords
- **⚠️ Allergen Safety:** Automatic filtering based on user allergen preferences
- **🧠 Context Awareness:** Maintains conversation context across multiple turns
- **📊 Nutrition Tracking:** Comprehensive nutrition facts with confidence scoring
- **🎯 Intent Recognition:** Understands complex multi-part queries

---

## Technology Stack

### Backend
- **Framework:** FastAPI (Python 3.10+)
- **AI/ML:**
  - LangGraph 1.0.1 (conversation orchestration)
  - LangChain 0.3.27 (LLM integration)
  - OpenAI APIs (GPT-4o-mini, text-embedding-3-large)
  - FAISS (vector similarity search)
- **Database:** MongoDB
- **Authentication:** JWT with bcrypt password hashing
- **Testing:** pytest with coverage reporting

### Frontend
- **Framework:** React 19.1.1 with TypeScript
- **Build Tool:** Vite 7.1.7
- **Routing:** React Router DOM 7.9.4
- **Styling:** Tailwind CSS
- **Testing:** Vitest with React Testing Library

### Infrastructure
- **Backend Deployment:** Render ([https://safebites-yu1o.onrender.com](https://safebites-yu1o.onrender.com))
- **Frontend Deployment:** Vercel ([https://se-wolfcafe.vercel.app](https://se-wolfcafe.vercel.app))
- **Database:** MongoDB Atlas

---

## Features

### Core Features
✅ **User Authentication & Profile Management**
- Secure signup/login with JWT tokens
- Password hashing with bcrypt
- Allergen preference management
- Profile updates and account deletion

✅ **Restaurant & Menu Management**
- Full CRUD operations for restaurants
- Bulk menu upload via CSV
- Dish enrichment using LLM (auto-populate missing data)
- Menu browsing and filtering

✅ **AI-Powered Conversational Search**
- Natural language query processing
- Multi-intent extraction (menu_search, dish_info, user_preferences, irrelevant)
- Context resolution across conversation turns
- Semantic search with FAISS vector embeddings
- Complex query handling ("Show me vegan pizzas and tell me the calories in margherita")

✅ **Allergen Safety System**
- 9 supported allergen types (peanuts, tree nuts, dairy, eggs, soy, wheat, fish, shellfish, sesame)
- Confidence scoring for detected allergens
- Automatic safety filtering on all results
- Visual safety indicators in UI

✅ **Nutrition & Health Tracking**
- Comprehensive nutrition facts (calories, protein, fat, carbs, sugar, fiber)
- Confidence scoring for estimates
- Query-based filtering ("dishes under 500 calories")

✅ **Advanced Filtering**
- Price range filtering
- Ingredient-based include/exclude filters
- Allergen-free filtering
- Nutrition-based filtering

### Technical Features
- **LangGraph Pipeline:** 7-node conversation state machine
- **Response Synthesis:** Structured JSON output aggregation
- **Session Management:** Persistent chat history in MongoDB
- **Background Processing:** Async menu processing and FAISS updates
- **Comprehensive Logging:** Multi-level rotating file logs
- **API Documentation:** Auto-generated OpenAPI docs at `/docs`
- **Test Coverage:** Unit and integration tests for backend/frontend

---

## Quick Start

### Prerequisites
- Python 3.10 or higher
- Node.js 18+ and npm
- MongoDB (local or Atlas)
- OpenAI API key

### Backend Setup

```bash
# Navigate to backend directory
cd proj2/SafeBites/backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << EOL
MONGO_URI=mongodb://localhost:27017
DB_NAME=foodapp
TEST_DB_NAME=foodapp_test
OPENAI_API_KEY=your_openai_api_key_here
JWT_SECRET=your_secret_key_here
EOL

# Run the server
uvicorn app.main:app --reload
```

Backend will be available at `http://localhost:8000`
- API docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Frontend Setup

```bash
# Navigate to frontend directory
cd proj2/SafeBites/frontend

# Install dependencies
npm install

# Create environment file
echo "VITE_API_BASE_URL=http://localhost:8000" > .env.local

# Start development server
npm run dev
```

Frontend will be available at `http://localhost:5173`

### Database Setup

If using MongoDB locally:
```bash
# Start MongoDB service
mongod --dbpath /path/to/your/data

# Or use Docker
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

If using MongoDB Atlas:
1. Create a cluster at [cloud.mongodb.com](https://cloud.mongodb.com)
2. Get your connection string
3. Update `MONGO_URI` in `.env`

---

## Project Structure

```
CSC_510_Proj3/
│
├── README.md                       # This file
│
└── proj2/SafeBites/
    │
    ├── backend/                    # Python FastAPI backend
    │   ├── app/
    │   │   ├── models/             # Pydantic data models
    │   │   ├── routers/            # API endpoint definitions
    │   │   ├── services/           # Business logic layer
    │   │   ├── flow/               # LangGraph conversation pipeline
    │   │   ├── utils/              # Helper utilities
    │   │   ├── tests/              # Test suite
    │   │   ├── logs/               # Application logs
    │   │   ├── config.py           # Configuration & logging
    │   │   ├── db.py               # MongoDB connection
    │   │   └── main.py             # FastAPI app entry point
    │   └── requirements.txt        # Python dependencies
    │
    ├── frontend/                   # React TypeScript frontend
    │   ├── src/
    │   │   ├── pages/              # Page components
    │   │   ├── frontend_test/      # Test files
    │   │   ├── assets/             # Static assets
    │   │   ├── App.tsx             # Root component
    │   │   └── main.tsx            # React entry point
    │   ├── package.json            # Node dependencies
    │   └── vite.config.ts          # Vite configuration
    │
    └── docs/                       # Documentation
        ├── features.md             # Comprehensive feature list
        ├── getting_started.md      # Detailed setup guide
        ├── CONTRIBUTING.md         # Contribution guidelines
        ├── CODE_OF_CONDUCT.md      # Code of conduct
        └── SELF_ASSESSMENT.md      # Project rubric mapping
```

---

## API Documentation

### User Endpoints
```
POST   /users/signup              - Register new user
POST   /users/login               - Authenticate user
GET    /users/me                  - Get current user profile (auth required)
PUT    /users/me                  - Update user profile (auth required)
DELETE /users/me                  - Delete user account (auth required)
GET    /users/{id_or_username}    - Get user by ID or username
```

### Restaurant Endpoints
```
POST   /restaurants/              - Create restaurant with menu CSV
GET    /restaurants/              - List all restaurants
GET    /restaurants/{id}          - Get restaurant details
PATCH  /restaurants/{id}          - Update restaurant info
DELETE /restaurants/{id}          - Delete restaurant
POST   /restaurants/search        - AI-powered chat search
GET    /restaurants/history/{user_id}/{restaurant_id} - Get chat history
```

### Dish Endpoints
```
POST   /dishes/{restaurant_id}    - Create dish
GET    /dishes/                   - List dishes with filters
GET    /dishes/filter             - Filter by allergens & restaurant
GET    /dishes/{dish_id}          - Get dish details
PUT    /dishes/{dish_id}          - Update dish
DELETE /dishes/{dish_id}          - Delete dish
```

For full API documentation, visit `/docs` after starting the backend server.

---

## Usage Examples

### Conversational Search

```
User: "Show me vegan pizzas"
Bot: [Lists 5 vegan pizza options]

User: "Under $15?"
Bot: [Filters to pizzas under $15]

User: "What are the calories in the margherita?"
Bot: "Margherita Pizza: 250 calories, 12g protein, 9g fat"

User: "What am I allergic to?"
Bot: "You have the following allergen preferences: peanuts, dairy, shellfish"
```

### Complex Multi-Intent Queries

```
User: "Show me high protein dishes under 500 calories and tell me if the Greek salad has dairy"

Response:
{
  "responses": [
    {
      "query": "high protein dishes under 500 calories",
      "type": "menu_search",
      "result": [/* dish list */]
    },
    {
      "query": "does Greek salad have dairy",
      "type": "dish_info",
      "result": {
        "dish_name": "Greek Salad",
        "allergens": ["dairy"],
        "why": "Contains feta cheese"
      }
    }
  ]
}
```

---

## Testing

### Backend Tests
```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test types
pytest -m unit
pytest -m integration

# Run specific test file
pytest tests/unit/test_intent_service.py
```

### Frontend Tests
```bash
cd frontend

# Run all tests
npm run test

# Watch mode
npm run test -- --watch

# UI test interface
npm run test:ui

# Coverage report
npm run test -- --coverage
```

---

## Environment Variables

### Backend (.env)
```env
# MongoDB Configuration
MONGO_URI=mongodb://localhost:27017           # MongoDB connection string
DB_NAME=foodapp                                # Database name
TEST_DB_NAME=foodapp_test                      # Test database name

# OpenAI Configuration
OPENAI_API_KEY=sk-...                          # OpenAI API key

# Authentication (optional)
JWT_SECRET=your_secret_key_here                # JWT signing secret
```

### Frontend (.env.local)
```env
VITE_API_BASE_URL=http://localhost:8000        # Backend API URL
```

---

## LangGraph Conversation Pipeline

SafeBites uses a sophisticated 7-node LangGraph pipeline for processing user queries:

```
┌─────────────────────┐
│  1. User Query      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 2. Context Resolver │ → Resolves "that dish", "it", etc.
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 3. Intent Classifier│ → Extracts menu_search, dish_info, etc.
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 4. Query Generator  │ → Organizes intents into structured queries
└──────────┬──────────┘
           │
     ┌─────┴─────┐
     ▼           ▼
┌─────────┐  ┌────────────┐
│5. Menu  │  │6. Dish Info│ → Parallel retrieval
│Retriever│  │ Retriever  │
└────┬────┘  └─────┬──────┘
     │            │
     └──────┬─────┘
            ▼
    ┌───────────────┐
    │7. Response    │ → Formats final JSON
    │  Synthesizer  │
    └───────────────┘
```

---

## Key Technologies Explained

### LangGraph
State machine framework for building complex LLM workflows. Manages conversation flow through nodes and conditional edges.

### LangChain
Framework for LLM integration. Provides prompt templates, chains, and tool integrations.

### FAISS
Facebook's vector similarity search library. Enables semantic search by finding similar dish embeddings.

### OpenAI Embeddings
Converts text to 1536-dimensional vectors capturing semantic meaning. Model: `text-embedding-3-large`

### FastAPI
Modern Python web framework with automatic API documentation and async support.

### React 19
Latest React with improved performance and concurrent rendering features.

### MongoDB
NoSQL document database perfect for flexible schema requirements.

---

## Deployment

### Backend (Render)
1. Connect GitHub repository to Render
2. Set environment variables in dashboard
3. Deploy from `backend/` directory
4. Set build command: `pip install -r requirements.txt`
5. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Frontend (Vercel)
1. Connect GitHub repository to Vercel
2. Set root directory to `frontend/`
3. Set environment variable `VITE_API_BASE_URL`
4. Deploy automatically on push to main

---

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](proj2/SafeBites/docs/CONTRIBUTING.md) for guidelines on:
- Code style and standards
- Branching strategy
- Commit message conventions
- Pull request process
- Testing requirements

---

## Code of Conduct

This project adheres to a Code of Conduct. Please read [CODE_OF_CONDUCT.md](proj2/SafeBites/docs/CODE_OF_CONDUCT.md) before contributing.

---

## Documentation

Comprehensive documentation available in `proj2/SafeBites/docs/`:
- **[features.md](proj2/SafeBites/docs/features.md)** - Detailed feature list with technical details
- **[getting_started.md](proj2/SafeBites/docs/getting_started.md)** - Step-by-step setup and development guide
- **[CONTRIBUTING.md](proj2/SafeBites/docs/CONTRIBUTING.md)** - Contribution guidelines
- **[CODE_OF_CONDUCT.md](proj2/SafeBites/docs/CODE_OF_CONDUCT.md)** - Community standards
- **[SELF_ASSESSMENT.md](proj2/SafeBites/docs/SELF_ASSESSMENT.md)** - Project rubric mapping

---

## Troubleshooting

### Common Issues

**Backend won't start:**
- Check MongoDB is running: `mongod --version`
- Verify `.env` file exists with correct variables
- Check Python version: `python --version` (should be 3.10+)

**Frontend can't connect to backend:**
- Ensure backend is running on `http://localhost:8000`
- Check `VITE_API_BASE_URL` in `.env.local`
- Verify CORS settings in `backend/app/main.py`

**FAISS index errors:**
- Delete `backend/faiss_index_restaurant/` directory
- Restart backend to rebuild index
- Ensure OpenAI API key is valid

**MongoDB connection errors:**
- Check MongoDB service is running
- Verify `MONGO_URI` connection string
- Check firewall/network settings

---

## Performance Considerations

- **FAISS Index:** Rebuilt automatically on menu uploads (async)
- **Embeddings:** Cached for previously processed dishes
- **Database Queries:** Optimized with MongoDB indexes
- **API Response Time:** Typically <2 seconds for complex queries
- **Concurrent Users:** Supports 100+ simultaneous users

---

## Security

- **Password Storage:** bcrypt hashing with salt rounds
- **Authentication:** JWT tokens with expiration
- **API Security:** Rate limiting, CORS protection
- **Input Validation:** Pydantic models validate all inputs
- **SQL Injection:** N/A (NoSQL database)
- **XSS Protection:** React auto-escapes user content

---

## License

This project is licensed under the MIT License. See LICENSE file for details.

---

## Team

**Project Lead:**
- Khush Patel
- Richa Jha

**Backend Development:**
- Khush Patel (LangGraph, FAISS, API)
- Richa Jha (Services, Models, Testing)

**Frontend Development:**
- Mia Glen (React components, UI/UX)
- Ishwarya (Styling, Testing)

---

## Acknowledgments

- **OpenAI** - GPT models and embeddings
- **LangChain Team** - LangGraph and LangChain frameworks
- **Facebook AI** - FAISS vector search library
- **FastAPI** - Modern Python web framework
- **React Team** - Frontend framework

---

## Roadmap (Project 3)

### Planned Features
- 🔮 **Personalized Recommender** - ML-based dish recommendations using user embeddings
- 🛒 **Chat-based Ordering** - Place orders through conversational interface
- 🚚 **Delivery Tracking** - Real-time order tracking dashboard
- 📊 **Admin Analytics** - Restaurant owner insights and analytics

---

## Support

For bugs, feature requests, or questions:
- **GitHub Issues:** [Create an issue](https://github.com/yourusername/safebites/issues)
- **Email:** support@safebites.com
- **Documentation:** See `docs/` directory

---

## Stats

- **Lines of Code:** 15,000+
- **API Endpoints:** 20+
- **Test Coverage:** 85%+
- **Supported Allergens:** 9
- **Intent Types:** 4
- **LangGraph Nodes:** 7
- **Database Collections:** 5

---

**Built with ❤️ using AI, Python, and React**

**Last Updated:** December 2025
**Version:** 2.0 (Project 2)

---

## Quick Links

- 🌐 [Live Demo](https://se-wolfcafe.vercel.app)
- 📚 [API Documentation](https://safebites-yu1o.onrender.com/docs)
- 📖 [Full Documentation](proj2/SafeBites/docs/)
- 🐛 [Report Bug](https://github.com/yourusername/safebites/issues)
- 💡 [Request Feature](https://github.com/yourusername/safebites/issues)

---

**Made for CSC 510 - Software Engineering**
**North Carolina State University**
**Fall 2025**
