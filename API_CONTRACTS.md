# API CONTRACTS — DATAFIX ENGINE

## 1. General Configuration

- **Base URL:** `http://127.0.0.1:8000`
- **API Prefix:** `/api`
- **Data Format:** JSON
- **Frontend Mount:** `/` (Web Dashboard) and `/static` (Static Assets)

---

## 2. Standard Response Structure

### Success Response
```json
{
  "success": true,
  "message": "Operation completed successfully",
  "data": {}
}
```

### Error Response
```json
{
  "success": false,
  "message": "An error occurred during execution",
  "errors": []
}
```

---

## 3. Implemented Endpoints

### 3.1 Health Check
- **Endpoint:** `GET /api/health`
- **Purpose:** System readiness and status telemetry.

### 3.2 Ingestion & Upload
- **Endpoint:** `POST /api/upload/single`
  - **Body:** `{ "name": "...", "registrationNumber": "...", "age": 20, "phoneNumber": "...", "department": "...", "semester": "4", "section": "A" }`
- **Endpoint:** `POST /api/upload/file`
  - **Body:** Multipart `file` (CSV / JSON)
- **Endpoint:** `GET /api/upload/current`
  - **Purpose:** Retrieves currently loaded dataset.
- **Endpoint:** `POST /api/upload/reset-college-sample`
  - **Purpose:** Loads 8-student benchmark dataset containing realistic errors for judging.

### 3.3 Anomaly Detection
- **Endpoint:** `GET /api/detection/run`
  - **Response Data:**
    - `totalRecords`: integer
    - `cleanRecords`: integer
    - `anomalousRecords`: integer
    - `purityPercentage`: float (0.0 – 100.0)
    - `anomalies`: list of anomaly items with `errorType`, `severity`, `field`, `suggestedFix`
    - `metrics`: speedometer telemetry (`speedometerMph`, `rpm`, `zone`, `status`, `boostLevel`)

### 3.4 Root Cause Diagnosis
- **Endpoint:** `GET /api/diagnosis/report`
  - **Response Data:** `healthStatus`, `anomalyBreakdown` (duplicates, formatErrors, missingValues, outliers), `aiRecommendations`.

### 3.5 Autonomous Repair Engine
- **Endpoint:** `POST /api/repair/auto`
  - **Response Data:**
    - `totalRepaired`: integer
    - `repairedRecords`: array of repaired records
    - `auditTrail`: list of repair diffs (`field`, `originalValue`, `repairedValue`, `strategy`)
    - `finalPurityPercentage`: float (boosted to 99–100%)

### 3.6 Quality Validation & Readiness
- **Endpoint:** `GET /api/validation/check`
  - **Response Data:** `isReady`, `overallPurity`, `checksPassed`, `certification` (`DATAFIX_CERTIFIED_CLEAN`).

### 3.7 Reports & Filtered Export
- **Endpoint:** `GET /api/reports/certificate`
  - **Purpose:** Official Quality Audit Certificate metadata.
- **Endpoint:** `POST /api/reports/export`
  - **Body:** `{ "filterType": "all" | "department" | "class", "targetValue": "...", "format": "csv" | "json" }`
  - **Response:** File attachment stream (CSV / JSON).

### 3.8 Audit History
- **Endpoint:** `GET /api/history/all`
  - **Purpose:** Complete chronological log of all ingestion, detection, and repair events.

---

## 4. Standard Session-Based API Contracts

### 4.1 Health Check
- **Endpoint:** `GET /health` or `GET /api/health`
- **Response:**
  ```json
  {
    "success": true,
    "message": "DataFix API is running.",
    "timestamp": "2026-11-19T14:40:00.000Z",
    "version": "1.0.0"
  }
  ```

### 4.2 Upload File
- **Endpoint:** `POST /upload` or `POST /api/upload`
- **Content-Type:** `multipart/form-data`
- **Body:** `file` (CSV or XLSX, max 10MB)
- **Response Data:** `sessionId`, `qualityScore`, `issueCount`, `issues` (`type`, `field`, `severity`, `affectedCount`, `suggestedFix`), `columns`, `rowCount`, `columnCount`, `fileType`, `status`.

### 4.3 Get Analysis
- **Endpoint:** `GET /analysis/:sessionId` or `GET /api/analysis/:sessionId`
- **Response Data:** `sessionId`, `qualityScore`, `issues`, `columns`, `aiInsights`, `repairs`, `rowCount`, `columnCount`, `status`.

### 4.4 Generate AI Insights
- **Endpoint:** `POST /analysis/:sessionId/ai-insights` or `POST /api/analysis/:sessionId/ai-insights`
- **Response Data:** `aiInsights`, `rootCauses`, `riskAssessment`, `priorityOrder`.

### 4.5 Apply Repair
- **Endpoint:** `POST /repair/:sessionId` or `POST /api/repair/:sessionId`
- **Body:** `{ "repairOptions": { "fixMissing": true, "removeDuplicates": true, "fixFormats": true, "fixOutliers": false } }`
- **Response Data:** `repairedRowCount`, `repairCount`, `newQualityScore`, `remainingIssues`, `repairLog`, `aiExplanation`.

### 4.6 Get Diff
- **Endpoint:** `GET /repair/:sessionId/diff` or `GET /api/repair/:sessionId/diff`
- **Response Data:** `original`, `repaired`, `changes` (`rowIndex`, `field`, `original`, `fixed`), `totalChanges`.

### 4.7 Download Repaired File
- **Endpoint:** `GET /download/:sessionId?format=csv` (or `xlsx`)
- **Query Params:** `format` (`csv` or `xlsx`)
- **Response:** Binary file download with attachment header.

### 4.8 Get Report
- **Endpoint:** `GET /report/:sessionId` or `GET /api/report/:sessionId`
- **Response Data:** `qualityScore`, `totalIssues`, `issuesByType`, `issuesBySeverity`, `columnAnalysis`, `repairSummary`, `aiInsights`, `timeline`.