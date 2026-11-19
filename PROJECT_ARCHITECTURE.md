# PROJECT ARCHITECTURE

## 1. Project Overview

**Project Name:** Data_Fix

**Description:** Autonomous Data Quality & Repair Engine with high-performance car speedometer booster telemetry, 3D scroll-triggered WebGL parallax pipeline, and interactive college/organization database intake and filtered repair export.

## 2. Technology Stack

### Frontend
- Architecture: Component-oriented HTML5 Single-Page Application (SPA)
- Styling: Custom Neon Cyber HUD & Glassmorphism CSS (`speedometer.css`, `style.css`)
- 3D Graphics: Three.js WebGL Engine (scroll-triggered dynamic pipeline)
- Audio: Native Web Audio API synthesized nitro and engine rumble SFX
- Telemetry: Dynamic SVG speedometer gauge (0–160 MPH scale) & RPM tachometer
- Compatibility: Runs both via FastAPI static file server (`http://localhost:8000/`) and standalone in any browser (`index.html`)

### Backend
- Runtime: Python 3.14
- Framework: FastAPI + Uvicorn
- Data Validation: Pydantic v2
- Storage: In-Memory / Document Repository with College Benchmark dataset

## 3. Project Folder Structure

```
Data_Fix/
│
├── frontend/
│   ├── css/
│   │   ├── speedometer.css
│   │   └── style.css
│   ├── js/
│   │   ├── threeScene.js
│   │   ├── speedometer.js
│   │   ├── collegeData.js
│   │   ├── sampleDatasets.js
│   │   ├── api.js
│   │   └── app.js
│   └── index.html
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── api/
│   │   │   ├── upload.py
│   │   │   ├── detection.py
│   │   │   ├── diagnosis.py
│   │   │   ├── repair.py
│   │   │   ├── validation.py
│   │   │   ├── reports.py
│   │   │   └── history.py
│   │   ├── services/
│   │   │   ├── file_service.py
│   │   │   ├── data_processor.py
│   │   │   ├── detection_service.py
│   │   │   ├── diagnosis_service.py
│   │   │   ├── repair_service.py
│   │   │   ├── validation_service.py
│   │   │   └── report_service.py
│   │   ├── models/
│   │   │   └── database_models.py
│   │   ├── schemas/
│   │   │   └── response_schemas.py
│   │   └── utils/
│   │       ├── file_utils.py
│   │       └── quality_metrics.py
│
├── AI_INSTRUCTIONS.md
├── PROJECT_ARCHITECTURE.md
├── API_CONTRACTS.md
├── .env.example
├── .gitignore
└── README.md
```

## 4. Architecture Explanation

### Frontend
- `threeScene.js`: 3D WebGL background tracking scroll progress through 4 visual pipeline stages (Chaotic cubes -> Swirling AI vortex -> Laser repair core -> Structured database cylinder).
- `speedometer.js`: Needle angle interpolation, RPM tachometer bar state, nitro booster activation, and Web Audio SFX synthesis.
- `sampleDatasets.js`: Pre-configured benchmark datasets (E-commerce customer CRM, University admissions, Healthcare clinical registry) for 1-click testing.
- `api.js`: Unified API connector targeting FastAPI backend with seamless offline JavaScript fallback and 8-endpoint contract support.
- `app.js`: Master UI coordinator for the 5-step autonomous quality workflow (Upload, Audit, AI Insights, Repair & Diff, Certification & Clean Export).

### Backend
- `main.py`: Configures FastAPI, CORS middleware, mounts `/static` assets, and serves `frontend/index.html` at root `/`.
- `api/`: Modular routers for ingestion (`/upload`), detection (`/detection`), diagnosis (`/diagnosis`), auto-repair (`/repair`), validation (`/validation`), reports (`/reports`), and audit history (`/history`).
- `services/`: Encapsulates business logic, data sanitization, anomaly detection algorithms, heuristic repair pipelines, and certification generation.

## 5. Development Commands

### Start FastAPI Application (Serving API + Frontend)
```powershell
py -3.14 -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

### Access Application
- Web Dashboard: `http://127.0.0.1:8000/`
- Interactive API Docs (Swagger): `http://127.0.0.1:8000/docs`