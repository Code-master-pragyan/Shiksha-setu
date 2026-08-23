# ShikshaSetu AI - Backend

## 1. Project Purpose
This is the backend for ShikshaSetu AI, an AI-powered personalized education platform.
*Note: Phase 0 only contains the backend foundation.*

## 2. Backend Technology Stack
- Python 3.11+
- FastAPI
- uvicorn
- pytest

## 3. Prerequisites
- Python 3.11 or higher
- Git

## 4. How to Create a Virtual Environment
Navigate to the `backend` directory and run:
```bash
python -m venv venv
```

## 5. How to Activate it on Windows
```powershell
venv\Scripts\activate
```

## 6. How to Activate it on Linux/macOS
```bash
source venv/bin/activate
```

## 7. How to Install Dependencies
```bash
pip install -r requirements.txt
```

## 8. How to Run the FastAPI Server
```bash
uvicorn app.main:app --reload
```

## 9. Health Endpoint
Once the server is running, you can verify it by visiting:
http://127.0.0.1:8000/health

Expected response:
```json
{
  "status": "ok"
}
```

## 10. Current Project Status
- Phase 0: Basic project structure, FastAPI setup, and health check endpoint.
