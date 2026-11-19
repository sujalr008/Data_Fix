# DataFix — Project Architecture

## Overview

**DataFix** is a full-stack Autonomous Data Quality & Repair Engine. It accepts CSV/XLSX files, detects data quality issues, applies AI-assisted repairs, and returns downloadable clean datasets with detailed reports.

---

## Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18 + Vite + Tailwind CSS |
| Backend | Node.js 20 + Express 5 |
| Database | MongoDB (Mongoose ODM) |
| AI | Google Gemini 1.5 Flash |
| File parsing | csv-parser, xlsx |
| File export | xlsx, csv-stringify |

---

## Directory Structure

```
Data_Fix/
├── backend/
│   ├── server.js              Entry point — bootstraps DB + HTTP server
│   ├── app.js                 Express app factory (middleware, routes)
│   ├── package.json
│   ├── .env                   PORT, MONGODB_URI, AI_API_KEY, FRONTEND_URL
│   └── src/
│       ├── config/
│       │   ├── database.js    Mongoose connection with retry logic
│       │   └── aiConfig.js    Gemini SDK initialisation
│       ├── models/
│       │   └── Session.js     Mongoose schema for a processing session
│       ├── routes/
│       │   ├── index.js       Mounts all sub-routers + health check
│       │   ├── uploadRoutes.js
│       │   ├── analysisRoutes.js
│       │   ├── repairRoutes.js
│       │   ├── downloadRoutes.js
│       │   └── reportRoutes.js
│       ├── controllers/
│       │   ├── uploadController.js
│       │   ├── analysisController.js
│       │   ├── repairController.js
│       │   ├── downloadController.js
│       │   └── reportController.js
│       ├── middleware/
│       │   ├── errorHandler.js    Global Express error handler
│       │   └── uploadMiddleware.js  Multer config (10 MB, CSV/XLSX only)
│       └── services/
│           ├── fileParserService.js   CSV/XLSX → JS array
│           ├── dataQualityService.js  Issue detection + quality scoring
│           ├── repairService.js       Rule-based repair strategies
│           └── ai/
│               └── geminiService.js  Gemini prompt builder + response parser
├── frontend/
│   ├── index.html
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── .env                   VITE_API_BASE_URL=http://localhost:5000/api
│   └── src/
│       ├── main.jsx
│       ├── App.jsx
│       ├── index.css
│       ├── context/
│       │   └── SessionContext.jsx
│       ├── hooks/
│       │   ├── useSession.js
│       │   └── useUpload.js
│       ├── services/
│       │   └── api.js          Axios instance + typed API helpers
│       ├── pages/
│       │   ├── LandingPage.jsx
│       │   ├── AnalysisPage.jsx
│       │   ├── RepairPage.jsx
│       │   ├── DiffPage.jsx
│       │   ├── ReportPage.jsx
│       │   └── DownloadPage.jsx
│       └── components/
│           ├── layout/
│           │   └── Navbar.jsx
│           ├── ui/
│           │   ├── QualityGauge.jsx
│           │   ├── IssueCard.jsx
│           │   ├── RepairCard.jsx
│           │   ├── DataTable.jsx
│           │   ├── DiffViewer.jsx
│           │   ├── LoadingSpinner.jsx
│           │   ├── AnimatedCounter.jsx
│           │   └── ColumnHealthBar.jsx
│           ├── upload/
│           │   └── DropZone.jsx
│           └── charts/
│               ├── IssueTypeChart.jsx
│               └── SeverityPieChart.jsx
└── API_CONTRACTS.md
```

---

## Data Flow

```
User uploads file (CSV/XLSX)
        │
        ▼
POST /api/upload
  uploadMiddleware (Multer, 10 MB limit)
  uploadController
    → fileParserService    (parse rows)
    → dataQualityService   (score + detect issues)
    → Session.create()     (persist in MongoDB)
        │
        ▼
GET /api/analysis/:sessionId
  analysisController → Session.findById()

POST /api/analysis/:sessionId/ai-insights
  analysisController → geminiService → Gemini 1.5 Flash → Session.update()

POST /api/repair/:sessionId
  repairController
    → repairService        (apply strategies)
    → geminiService        (AI explanation)
    → Session.update()

GET /api/repair/:sessionId/diff
  repairController → Session (original vs repaired)

GET /api/download/:sessionId?format=csv|xlsx
  downloadController → xlsx / csv-stringify → file stream

GET /api/report/:sessionId
  reportController → aggregate session data → report object
```

---

## Session Model (MongoDB)

```
Session {
  _id:            ObjectId
  originalData:   Array<Object>   // raw parsed rows
  repairedData:   Array<Object>   // post-repair rows
  columns:        [String]
  rowCount:       Number
  columnCount:    Number
  fileType:       "csv" | "xlsx"
  qualityScore:   Number (0–100)
  issues:         [IssueObject]
  repairs:        [RepairLogEntry]
  aiInsights:     String
  status:         "uploaded" | "analysed" | "repaired"
  createdAt:      Date
  updatedAt:      Date
}
```

---

## Middleware Stack (app.js)

| Order | Middleware | Purpose |
|-------|-----------|---------|
| 1 | `helmet` | Security headers |
| 2 | `cors` | Allow localhost:3000 + 5173 + FRONTEND_URL |
| 3 | `express.json` | JSON body parsing (5 MB) |
| 4 | `express-rate-limit` (global) | 200 req / 15 min |
| 5 | `express-rate-limit` (upload) | 20 req / 10 min |
| 6 | API Router | All `/api/*` routes |
| 7 | `errorHandler` | Catches & formats all thrown errors |

---

## Environment Variables

### Backend (`.env`)

| Variable | Example | Description |
|----------|---------|-------------|
| `PORT` | `5000` | HTTP server port |
| `MONGODB_URI` | `mongodb://localhost:27017/datafix` | MongoDB connection string |
| `AI_API_KEY` | `AIza...` | Google Gemini API key |
| `AI_MODEL` | `gemini-1.5-flash` | Gemini model identifier |
| `AI_PROVIDER` | `google` | AI provider tag |
| `FRONTEND_URL` | `http://localhost:5173` | CORS allowed origin |

### Frontend (`.env`)

| Variable | Example | Description |
|----------|---------|-------------|
| `VITE_API_BASE_URL` | `http://localhost:5000/api` | Backend base URL |

---

## API Endpoints Summary

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/health` | Health check |
| POST | `/api/upload` | Upload & analyse file |
| GET | `/api/analysis/:sessionId` | Retrieve analysis |
| POST | `/api/analysis/:sessionId/ai-insights` | Generate AI insights |
| POST | `/api/repair/:sessionId` | Apply repairs |
| GET | `/api/repair/:sessionId/diff` | Get change diff |
| GET | `/api/download/:sessionId` | Download repaired file |
| GET | `/api/report/:sessionId` | Full quality report |

> See `API_CONTRACTS.md` for complete request/response schemas.

---

## Running Locally

```bash
# Backend
cd backend
cp .env.example .env   # fill in AI_API_KEY
npm install
npm run dev            # nodemon, port 5000

# Frontend
cd frontend
cp .env.example .env
npm install
npm run dev            # Vite, port 5173
```

**Prerequisites:** Node.js ≥ 18, MongoDB running locally on port 27017.
