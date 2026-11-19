# DataFix API Contracts

**Base URL:** `http://localhost:5000/api`

**Standard Response Envelope:**
```json
{ "success": true,  "message": "...", "data": { ... } }
{ "success": false, "message": "...", "errors": [] }
```

---

## 1. Health Check
### `GET /api/health`
Returns system readiness and status telemetry.

**Response `200`**
```json
{
  "success": true,
  "message": "DataFix API is running.",
  "timestamp": "2026-11-20T00:00:00.000Z",
  "version": "1.0.0"
}
```

---

## 2. Ingestion & Upload
### `POST /api/upload`
Upload a CSV or XLSX file for automated inspection and anomaly detection. Initiates a session.

**Request**
- Content-Type: `multipart/form-data`
- Field: `file` — CSV or XLSX file (max 10 MB)

**Response `200`**
```json
{
  "success": true,
  "message": "File uploaded and analysed successfully.",
  "data": {
    "sessionId": "6aff4094152ec058a105f3d9",
    "qualityScore": 78,
    "issueCount": 4,
    "issues": [
      {
        "type": "missing_values",
        "field": "email",
        "severity": "critical",
        "affectedCount": 5,
        "suggestedFix": "Impute with placeholder or drop rows"
      }
    ],
    "columns": ["id", "name", "email", "age"],
    "rowCount": 200,
    "columnCount": 4,
    "fileType": "csv",
    "status": "analysed"
  }
}
```

---

## 3. Analysis
### `GET /api/analysis/:sessionId`
Retrieve the full data quality analysis for an existing session.

**Path Parameters**
- `sessionId`: string (MongoDB ObjectId or Session ID)

**Response `200`**
```json
{
  "success": true,
  "message": "Analysis retrieved successfully.",
  "data": {
    "sessionId": "6aff4094152ec058a105f3d9",
    "qualityScore": 78,
    "issues": [
      { "type": "missing_values", "field": "email", "severity": "critical", "affectedCount": 5 }
    ],
    "columns": ["id", "name", "email", "age"],
    "aiInsights": null,
    "repairs": [],
    "rowCount": 200,
    "columnCount": 4,
    "status": "analysed"
  }
}
```

---

## 4. Root Cause Diagnosis & AI Insights
### `POST /api/analysis/:sessionId/ai-insights`
Trigger AI analysis (Groq / Gemini) to diagnose root causes, assess operational risks, and recommend prioritized remediation steps.

**Response `200`**
```json
{
  "success": true,
  "message": "AI insights generated.",
  "data": {
    "aiInsights": "The dataset contains several quality issues that may affect downstream analytics...",
    "rootCauses": [
      "Inconsistent client-side validation on email inputs",
      "Repeated ETL import batches causing duplicate records"
    ],
    "riskAssessment": "Critical — 7% of rows contain critical nulls in key identifiers.",
    "priorityOrder": [
      "Deduplicate exact-match records",
      "Impute missing values in key fields",
      "Standardise date formats to ISO 8601"
    ]
  }
}
```

---

## 5. Autonomous Repair Engine
### `POST /api/repair/:sessionId`
Apply automated, safe repair strategies to the dataset.

**Request Body**
```json
{
  "repairOptions": {
    "fixMissing": true,
    "removeDuplicates": true,
    "fixFormats": true,
    "fixOutliers": false
  }
}
```

**Response `200`**
```json
{
  "success": true,
  "message": "Data repaired successfully.",
  "data": {
    "repairedRowCount": 195,
    "repairCount": 12,
    "newQualityScore": 94,
    "remainingIssues": 0,
    "repairLog": [
      { "action": "imputed", "field": "email", "rowIndex": 3, "value": "N/A" },
      { "action": "removed_duplicate", "rowIndex": 7 }
    ],
    "aiExplanation": "12 repairs applied successfully. Missing values imputed; duplicate rows removed."
  }
}
```

---

## 6. Audit Trail & Diff
### `GET /api/repair/:sessionId/diff`
Retrieve a cell-by-cell delta comparing original vs repaired datasets.

**Response `200`**
```json
{
  "success": true,
  "message": "Diff retrieved successfully.",
  "data": {
    "original": [ { "id": 1, "name": " John ", "email": null } ],
    "repaired": [ { "id": 1, "name": "John", "email": "N/A" } ],
    "changes": [
      { "rowIndex": 0, "field": "name", "original": " John ", "fixed": "John" },
      { "rowIndex": 0, "field": "email", "original": null, "fixed": "N/A" }
    ],
    "totalChanges": 2
  }
}
```

---

## 7. Clean Dataset Export & Download
### `GET /api/download/:sessionId?format=csv` *(or `format=xlsx`)*
Download the clean, repaired dataset as a CSV or XLSX file.

**Response `200`**
- Content-Type: `text/csv` or `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
- Content-Disposition: `attachment; filename="datafix_repaired_<sessionId>.csv"`

---

## 8. Quality Certification & Report
### `GET /api/report/:sessionId`
Generate and return a comprehensive data quality scorecard and timeline.

**Response `200`**
```json
{
  "success": true,
  "message": "Report generated successfully.",
  "data": {
    "qualityScore": 94,
    "totalIssues": 14,
    "issuesByType": {
      "missing_values": 5,
      "duplicates": 3,
      "format_errors": 4,
      "outliers": 2
    },
    "issuesBySeverity": {
      "critical": 5,
      "high": 4,
      "medium": 3,
      "low": 2
    },
    "columnAnalysis": [
      { "column": "email", "issues": 5, "completeness": 97.5, "type": "string" }
    ],
    "repairSummary": {
      "totalRepairs": 12,
      "repairedRowCount": 195,
      "originalRowCount": 200
    },
    "aiInsights": "The dataset shows strong improvement after repair...",
    "timeline": {
      "uploadedAt": "2026-11-20T00:00:00.000Z",
      "analysedAt": "2026-11-20T00:00:02.000Z",
      "repairedAt": "2026-11-20T00:05:00.000Z"
    }
  }
}
```
