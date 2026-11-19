# DataFix — Project Architecture

## Overview

**DataFix** is a full-stack Autonomous Data Quality & Repair Engine. It accepts CSV/XLSX files, detects data quality issues, applies AI-assisted repairs, and returns downloadable clean datasets with detailed reports and audit trails.

---

## Stack

| Layer | Technology |
|---|---|
| Frontend | React / Tailwind CSS / Vanilla JS & Three.js 3D Visualizer |
| Backend | Python 3.15 + FastAPI + Uvicorn |
| Database | MongoDB Atlas (PyMongo) |
| AI | Groq API (`openai/gpt-oss-120b`) / Google Gemini Flash |
| Data Processing | Pandas, OpenpyXL, NumPy |

---

## Directory Structure

```
Data_Fix/
├── backend/
│   ├── main.py                     # FastAPI application bootstrap, CORS & route mounts
│   ├── requirements.txt            # Python dependencies
│   ├── .env                        # Environment configurations (PORT, MONGODB_URI, AI settings)
│   ├── test_api.py                 # Comprehensive E2E test suite covering all 8 endpoints
│   └── app/
│       ├── config.py               # Centralized configuration & environment loader
│       ├── database.py             # MongoDB connection with resilient fallback store
│       ├── models/
│       │   └── schemas.py          # Pydantic request/response models conforming to API contracts
│       ├── services/
│       │   ├── parser_service.py   # CSV/XLSX parser, exporter, and NaN sanitizer
│       │   ├── quality_service.py  # Issue detection & quality score engine
│       │   ├── repair_service.py   # Automated cleaning & repair strategies
│       │   ├── diff_service.py     # Row- and cell-level diff generator
│       │   ├── ai_service.py       # Groq & Gemini API client & intelligent analysis engine
│       │   └── report_service.py   # Full report aggregator
│       └── routes/
│           ├── health.py           # GET /api/health
│           ├── upload.py           # POST /api/upload
│           ├── analysis.py         # GET /api/analysis/{id}, POST /api/analysis/{id}/ai-insights
│           ├── repair.py           # POST /api/repair/{id}, GET /api/repair/{id}/diff
│           ├── download.py         # GET /api/download/{id}
│           ├── report.py           # GET /api/report/{id}
│           └── ui.py               # GET / (Unified single-page interactive dashboard)
├── frontend/
│   ├── index.html
│   ├── css/
│   │   ├── speedometer.css
│   │   └── style.css
│   ├── js/
│   │   ├── api.js
│   │   ├── app.js
│   │   ├── collegeData.js
│   │   ├── speedometer.js
│   │   └── threeScene.js
│   └── src/
│       └── services/
│           └── api.js              # Reusable API connector client
├── API_CONTRACTS.md
└── PROJECT_ARCHITECTURE.md
```

---

## Data Flow

```
User uploads file (CSV/XLSX)
        │
        ▼
POST /api/upload
  → parser_service    (parse rows, strip headers, sanitize NaNs)
  → quality_service   (detect missing, duplicates, format errors, outliers, calculate score)
  → database          (persist session doc in MongoDB Atlas)
        │
        ▼
GET /api/analysis/:sessionId
  → database.find_by_id()

POST /api/analysis/:sessionId/ai-insights
  → ai_service        (Groq GPT-OSS 120B / Gemini API root cause & risk analysis)
  → database.update()

POST /api/repair/:sessionId
  → repair_service    (safe imputation, deduplication, format standardization, outlier clipping)
  → database.update()

GET /api/repair/:sessionId/diff
  → diff_service      (cell-by-cell original vs repaired delta)

GET /api/download/:sessionId?format=csv|xlsx
  → parser_service    (binary file stream download)

GET /api/report/:sessionId
  → report_service    (scorecard, column analysis, repair summary, timeline)
```

---

## Running Locally

### Backend
```powershell
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 5000 --reload
```

- Web Dashboard: `http://localhost:5000/`
- Interactive API Docs (Swagger): `http://localhost:5000/docs`
