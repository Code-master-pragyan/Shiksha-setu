<div align="center">
  <h1>🌟 ShikshaSetu AI</h1>
  <p>An advanced, AI-powered personalized education platform</p>
  
  [![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
  [![Next.js](https://img.shields.io/badge/Next.js-black?style=for-the-badge&logo=next.js&logoColor=white)](https://nextjs.org/)
  [![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)](https://postgresql.org)
  [![pgvector](https://img.shields.io/badge/pgvector-Vector_Search-blue?style=for-the-badge)](https://github.com/pgvector/pgvector)
  [![Gemini](https://img.shields.io/badge/Gemini_AI-Google-orange?style=for-the-badge)](https://deepmind.google/technologies/gemini/)
</div>

---

## 📖 Overview

**ShikshaSetu AI** is a state-of-the-art educational platform designed to bridge the gap between traditional learning and modern, AI-driven personalization. It provides tailored learning experiences, answers student doubts dynamically, detects misconceptions, and empowers teachers with actionable insights.

The platform is built with a dual-focus:
1. **For Students:** An interactive dashboard, dynamic Doubt Solver, and Adaptive Practice.
2. **For Teachers:** Deep analytics, progress tracking, and cognitive insight into where students struggle.

---

## 🏗️ Architecture & Tech Stack

ShikshaSetu AI operates on a modern decoupled architecture:

### 1. Frontend (Next.js)
- **Framework:** Next.js (App Router) + React
- **Styling:** Tailwind CSS + Shadcn UI for beautiful, responsive components.
- **State Management:** Zustand for lightweight global state (authentication, active student context).
- **Animation:** Framer Motion for fluid micro-interactions and page transitions.

### 2. Backend (FastAPI)
- **Framework:** Python FastAPI for high-performance, asynchronous REST APIs.
- **ORM & Database:** SQLAlchemy 2.0 connecting to a Neon PostgreSQL database.
- **Authentication:** JWT (JSON Web Tokens) with Bcrypt password hashing.
- **Vector Search:** `pgvector` extension for storing and querying AI embeddings.

### 3. AI & RAG Engine (Google Gemini)
- **Embeddings:** `text-embedding-004` to convert curriculum knowledge chunks into high-dimensional vectors.
- **Generative AI:** `gemini-3.6-flash` (or `gemini-1.5-flash`) for synthesizing answers, generating adaptive questions, and conversational tutoring.

---

## ⚙️ Core Workflows: How It Works

### 1. Knowledge Ingestion (RAG System Setup)
Before the system can teach, it must learn the curriculum.
* **Process:** Textbooks (PDFs) are ingested via the `backend/scripts/ingest_knowledge.py` script.
* **Chunking & Embedding:** The text is chunked into logical semantic blocks. `gemini` creates vector embeddings for each chunk.
* **Storage:** Chunks and their vectors are saved to the `concepts` and `knowledge_chunks` tables in PostgreSQL.

### 2. The Doubt Solver (Retrieval-Augmented Generation)
When a student asks a question on the frontend:
1. The backend converts the user's question into a vector using the Gemini Embedding model.
2. `pgvector` performs a **Cosine Similarity Search** in the database to find the top 3 most relevant textbook chunks.
3. The context chunks and the user's question are sent to the Gemini Generative model with a strict system prompt (acting as an empathetic tutor).
4. The AI formulates a tailored response.

### 3. Adaptive Practice & Mastery Engine
* **Generation:** When a student enters "Practice", the backend retrieves their current mastery scores. It asks Gemini to generate a Multiple Choice Question tailored to their exact proficiency level (Beginner, Intermediate, or Advanced).
* **Evaluation:** When the student submits an answer, the backend evaluates it.
* **Mastery Updates:** An algorithm adjusts the student's mastery score for that specific concept based on correctness, utilizing a weighted moving average. 

### 4. Teacher Insights
Teachers have a dedicated dashboard that fetches aggregated data. The backend calculates classroom-wide strengths and identifies "At Risk" concepts by analyzing average mastery scores across all students.

---

## 🚀 Local Development Guide

### Prerequisites
- Python 3.9+
- Node.js 18+
- PostgreSQL database (or Neon DB) with `pgvector` enabled
- Google Gemini API Key

### Backend Setup
```bash
cd backend
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\activate
# Unix/MacOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Backend Configuration
Copy `.env.example` to `.env` and configure your credentials:
```bash
cp .env.example .env
```
Ensure you have set:
- `GEMINI_API_KEY`
- `DATABASE_URL`
- `JWT_SECRET_KEY`

### Database Initialization & Seeding
Initialize the database schemas and load the AI with textbook data:
```bash
# 1. Create tables
python scripts/init_db.py

# 2. Ingest PDFs into text chunks
python scripts/ingest_knowledge.py

# 3. Convert text chunks to vector embeddings
python scripts/embed_knowledge.py

# 4. Create demo students and teachers
python scripts/seed_demo_users.py
```

### Start the Backend Server
```bash
uvicorn app.main:app --reload
```
- API is live at: `http://127.0.0.1:8000`
- Interactive API Docs: `http://127.0.0.1:8000/docs`

---

### Frontend Setup
```bash
cd frontend
npm install
```

### Frontend Configuration
Copy `.env.example` to `.env.local`:
```bash
cp .env.example .env.local
```
Ensure it points to your local backend:
`NEXT_PUBLIC_API_URL=http://127.0.0.1:8000/api/v1`

### Start the Frontend Server
```bash
npm run dev
```
The frontend is live at `http://localhost:3000` (or 3001).

---

## 🌍 Production Deployment

ShikshaSetu AI is designed for seamless deployment on platforms like Vercel (Frontend) and Render/AWS (Backend).

### Backend Environment Variables (Production)
Do NOT commit these to git. Set them in your hosting provider's dashboard:
- `ENVIRONMENT=production`
- `DEBUG=false`
- `DATABASE_URL=<your_neon_production_db_url>`
- `TEST_DATABASE_URL=<optional_test_db>`
- `GEMINI_API_KEY=<your_api_key>`
- `JWT_SECRET_KEY=<your_secret_key>`
- `FRONTEND_URL=https://<your-vercel-app>.vercel.app`
- `CORS_ORIGINS=https://<your-vercel-app>.vercel.app`

### Frontend Environment Variables (Production)
- `NEXT_PUBLIC_API_URL=https://<your-backend-app>.onrender.com/api/v1`

**Build Commands:**
- **Frontend:** `npm run build` -> `npm start`
- **Backend:** `pip install -r requirements.txt` -> `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

---

## 🧪 Testing

We use `pytest` for backend testing. To protect your production and development data, testing requires a dedicated database.

1. Set `TEST_DATABASE_URL` in your `.env`.
2. Run tests:
```bash
cd backend
pytest -v
```

> **Security Guard:** The test suite will automatically abort if `ENVIRONMENT=production` is detected, ensuring production data is never accidentally wiped by test setup routines.
