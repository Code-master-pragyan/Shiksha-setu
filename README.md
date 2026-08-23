# ShikshaSetu AI

ShikshaSetu AI is an AI-powered personalized education platform designed to provide tailored learning experiences, answer student doubts, detect misconceptions, and empower teachers with actionable insights.

## Project Structure
The repository contains both frontend and backend code:
- `backend/`: Python backend powered by FastAPI.
- `frontend/`: Next.js frontend application.

## Local Development

### 1. Prerequisites
- Python 3.9+
- Node.js 18+
- PostgreSQL database (or Neon DB) with `pgvector` enabled
- Google Gemini API Key

### 2. Backend Setup
```bash
cd backend
python -m venv venv
# Activate virtual environment
# Windows:
.\venv\Scripts\activate
# Unix:
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Backend Configuration
Copy `.env.example` to `.env` and fill in the values:
```bash
cp .env.example .env
```
Ensure you have set:
- `GEMINI_API_KEY`
- `DATABASE_URL`
- `JWT_SECRET_KEY`

### 4. Database Setup & Seeding
Initialize the database and insert demo data:
```bash
# Apply schemas
python scripts/init_db.py

# Ingest and embed textbooks
python scripts/ingest_knowledge.py
python scripts/embed_knowledge.py

# Seed demo users
python scripts/seed_demo_users.py
```

### 5. Run FastAPI
```bash
uvicorn app.main:app --reload
```
The API runs at `http://127.0.0.1:8000`
Swagger Docs at `http://127.0.0.1:8000/docs`

### 6. Frontend Setup
```bash
cd frontend
npm install
```

### 7. Frontend Configuration
Copy `.env.example` to `.env.local`:
```bash
cp .env.example .env.local
```
Set `NEXT_PUBLIC_API_URL=http://127.0.0.1:8000`

### 8. Run Next.js
```bash
npm run dev
```
The frontend runs at `http://localhost:3000`

## Production Deployment Configuration

For production, provide the following environment variables through your deployment platform (do NOT commit these to git).

**Backend:**
- `DATABASE_URL=<production database URL>`
- `GEMINI_API_KEY=<Gemini API key>`
- `JWT_SECRET_KEY=<strong production secret>`
- `CORS_ORIGINS=<production frontend URL>`
- `ENVIRONMENT=production`
- `DEBUG=false`

**Frontend:**
- `NEXT_PUBLIC_API_URL=<production backend URL>`

To run the production frontend build:
```bash
npm run build
npm start
```

## Testing

To run the backend test suite safely, you must configure a dedicated test database to avoid data corruption in your development or production databases. 

1. Create a test PostgreSQL database.
2. In your backend `.env` file, set the `TEST_DATABASE_URL` variable:
```env
TEST_DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/shikshasetu_test
```
3. Run the tests using pytest:
```bash
cd backend
pytest -v
```

**Security Note:** 
- The test runner is strictly configured to **abort** if `ENVIRONMENT=production`.
- The production `DATABASE_URL` is protected and will never be used by `pytest`. Test execution will gracefully fail if `TEST_DATABASE_URL` is not provided.

## Local vs Production Configuration Matrix

| Setting | Development | Production | Testing |
|---------|-------------|------------|---------|
| Frontend API URL | `http://127.0.0.1:8000` | deployed backend URL | N/A |
| Environment | `development` | `production` | `development` |
| Debug | `true` | `false` | `true` |
| Database | development DB / Local | production DB (Neon/RDS) | test DB (TEST_DATABASE_URL) |
| CORS Origins | `http://localhost:3000` | deployed frontend URL | N/A |
| JWT Secret | local dev secret | secure random token | local dev secret |
