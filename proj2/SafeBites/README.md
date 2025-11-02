# 🍴 Food Delivery System – Local Development Setup
## Badges

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-Framework-brightgreen?logo=fastapi)
![MongoDB](https://img.shields.io/badge/Database-MongoDB-green?logo=mongodb)
![Docker](https://img.shields.io/badge/Container-Docker-blue?logo=docker)
![GitHub Actions](https://img.shields.io/github/actions/workflow/status/the-Shallow/SE-WOLFCAFE/python-app.yml?label=CI%20Build&logo=githubactions)
![Coverage](https://img.shields.io/codecov/c/github/the-Shallow/SE-WOLFCAFE?label=Coverage&logo=codecov)
![License](https://img.shields.io/github/license/the-Shallow/SE-WOLFCAFE)
![Contributions welcome](https://img.shields.io/badge/Contributions-welcome-brightgreen.svg)


![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-Framework-brightgreen?logo=fastapi)
![MongoDB](https://img.shields.io/badge/Database-MongoDB-green?logo=mongodb)
![Docker](https://img.shields.io/badge/Container-Docker-blue?logo=docker)
![GitHub Actions](https://img.shields.io/github/actions/workflow/status/the-Shallow/SE-WOLFCAFE/python-app.yml?label=CI%20Build&logo=githubactions)
![Coverage](https://img.shields.io/codecov/c/github/the-Shallow/SE-WOLFCAFE?label=Coverage&logo=codecov)
![License](https://img.shields.io/github/license/the-Shallow/SE-WOLFCAFE)
![Contributions welcome](https://img.shields.io/badge/Contributions-welcome-brightgreen.svg)


A full-stack AI-powered Food Delivery System that combines a React frontend with a FastAPI + Langgraph + MongoDB backend.

🚀 Features

<<<<<<< HEAD
🍽️ Restaurant & Menu Search — Natural language search using Langgraph & FAISS

🤖 AI Query Understanding — Extracts user intents and applies structured filters

💾 MongoDB Integration — Manages restaurants, dishes, and user profiles

⚡ FastAPI Backend — Modular and scalable REST API architecture

🎨 React Frontend — Interactive UI styled with TailwindCSS


🛠️ Prerequisites

Ensure the following are installed on your system:

Tool	Required Version	Description
Python
	3.10+	Backend runtime
pip / uv
	latest	Dependency manager
Node.js
	≥ 18	For running React frontend
MongoDB
	latest	Database (local or Atlas)
Git
	—	Version control


📁 Project Structure
food-delivery-system/
├── frontend/       # React + Tailwind app
├── backend/        # FastAPI + LangChain + MongoDB + FAISS
├── docs/        # Documentation
└── README.md

🎨 Frontend Setup
cd frontend
npm install
npm run dev


Runs the development server at http://localhost:5173/
 (default for Vite).

⚙️ Backend Setup
cd backend
python -m venv venv
# Activate virtual environment
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

🔐 Environment Variables

Create a .env file in the backend directory with:

MONGO_URI=your_mongodb_uri
OPENAI_API_KEY=your_openai_key
JWT_SECRET=your_secret_key

▶️ Run the Backend
uvicorn app.main:app --reload


Runs the API server at http://localhost:8000
.

🧩 Tech Stack Overview
Layer	Technology	Description
Frontend	React, CSS, Vite	Modern UI framework
Backend	FastAPI, LangChain, Langgraph & APIs
Database	MongoDB	NoSQL document storage
Vector Search	FAISS	Semantic retrieval for menu data
Language Model	OpenAI (or local model)	Query understanding & reasoning
🧠 Core Modules (Backend)
<!-- Module	Purpose
semantic_retrieve	Retrieves dishes using vector embeddings
intent_extraction	Extracts intents (e.g., “price < 20”, “vegan”)
metadata_filter	Applies structured constraints
validation	Ensures relevant dish matching
orchestrator	Coordinates multi-step reasoning -->
🧪 Running Tests
pytest


or run module-wise:

pytest tests/test_semantic_retrieve.py

🧰 Development Notes

Use modularized service, model, and router layers for maintainability.

<!-- Ensure all routes are prefixed under /api/v1. -->

Follow consistent naming (snake_case for backend, camelCase for frontend).

Keep embeddings and FAISS index files under backend/app/vector_store/.

🤝 Contributing

Contributions are welcome!
Create a feature branch and submit a pull request:

git checkout -b feature/your-feature
git push origin feature/your-feature

📜 License

This project is licensed under the MIT License.
=======
## Backend Setup
    cd backend
    python -m venv venv
    venv\Scripts\activate
    pip install -r requirements.txt
    Create .env file for storing private variables such as database urls, openAI api keys, jwt_secret.
    uvicorn app.main:app --reload

## Dish CRUD APIs implemented:
   1. POST   /dishes/               → Create a new dish
   2. GET    /dishes/{dish_id}      → Get dish by ID
   3. GET    /dishes/               → Get all dishes
   4. PUT    /dishes/{dish_id}      → Update a dish
   5. DELETE /dishes/{dish_id}      → Delete a dish

## User CRUD APIs implemented:
   1. POST   /users/signup          → Create new user
   2. POST   /users/login           → Login & get token
   3. GET    /users/me              → Get logged-in user profile
   4. PUT    /users/me              → Update profile
   5. DELETE /users/me              → Delete user
   6. GET    /users/{id}            → Get user by ID
>>>>>>> backend
