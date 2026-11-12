# BillKind AI - Complete Project Setup & Run Guide

AI-Powered Essential Bills Crowdfunding & Direct Financial Assistance Platform.

---

## 📁 Project Structure

```
BillKind_AI/
├── frontend/             # React 18 + Vite + Tailwind CSS + Lucide Icons
│   ├── src/
│   │   ├── App.tsx       # Main Single-Page Application (Full Workflow)
│   │   ├── main.tsx
│   │   └── ...
│   ├── package.json
│   └── vite.config.ts
├── backend/              # FastAPI + Python + SQLite
│   ├── app/
│   │   ├── main.py       # REST API endpoints & routes
│   │   ├── email_service.py # Gmail SMTP dispatch with RFC urgent headers
│   │   ├── database.py   # SQLite schema & password hashing
│   │   ├── billbridge.db # SQLite database
│   │   └── uploads/      # Uploaded bill documents & PDFs
│   └── .env              # Gmail SMTP credentials configuration
└── docs/                 # Complete Architecture & SRS Documentation
    ├── SRS.md
    ├── ARCHITECTURE.md
    ├── API.md
    ├── DATABASE.md
    ├── AI_PIPELINE.md
    ├── SECURITY.md
    └── ROADMAP.md
```

---

## 🚀 How to Run the Project

### 1. Start the Backend (FastAPI)

Open a terminal in `backend/app`:
```bash
cd backend/app
py -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
- API Health Check: `http://localhost:8000/`
- Interactive API Swagger Docs: `http://localhost:8000/docs`

---

### 2. Start the Frontend (Vite)

Open a second terminal in `frontend`:
```bash
cd frontend
npm install
npm run dev
```
- Web Application: `http://localhost:5173/`
