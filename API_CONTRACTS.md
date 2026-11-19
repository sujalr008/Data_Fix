# DataFix API Contracts

**Base URL:** `http://localhost:5000/api`

**Standard Response Envelope:**
```json
{ "success": true,  "message": "...", "data": { ... } }
{ "success": false, "message": "...", "errors": [] }
```

---

## Health Check

### `GET /api/health`

Returns server status.

**Response `200`**
```json
{
  "success": true,
  "message": "DataFix API is running.",
  "timestamp": "2024-01-01T00:00:00.000Z",
  "version": "1.0.0"
}
```

---

## Upload

### `POST /api/upload`

Upload a CSV or XLSX file for analysis. Initiates a new session.

**Request**
- Content-Type: `multipart/form-data`
- Field: `file` — CSV or XLSX file (max 10 MB)

**Response `200`**
```json
{
  "success": true,
  "message": "File uploaded and analysed successfully.",
  "data": {
    "sessionId": "64f1a2b3c4d5e6f7a8b9c0d1",
    "qualityScore": 78,
    "issueCount": 14,
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

**Errors**
| Code | Reason |
|------|--------|
| 400  | No file provided, unsupported file type |
| 413  | File exceeds 10 MB limit |
| 500  | Parse or storage error |

---

## Analysis

### `GET /api/analysis/:sessionId`

Retrieve the full analysis for an existing session.

**Path Parameters**
| Param | Type | Description |
|-------|------|-------------|
| `sessionId` | string | MongoDB ObjectId returned by `/upload` |

**Response `200`**
```json
{
  "success": true,
  "message": "Analysis retrieved successfully.",
  "data": {
    "sessionId": "64f1a2b3c4d5e6f7a8b9c0d1",
    "qualityScore": 78,
    "issues": [ { "type": "missing_values", "field": "email", "severity": "critical", "affectedCount": 5 } ],
    "columns": ["id", "name", "email", "age"],
    "aiInsights": null,
    "repairs": [],
    "rowCount": 200,
    "columnCount": 4,
    "status": "analysed"
  }
}
```

**Errors**
| Code | Reason |
|------|--------|
| 404  | Session not found |
| 500  | Database error |

---

### `POST /api/analysis/:sessionId/ai-insights`

Trigger Gemini AI analysis and persist insights on the session.

**Path Parameters**
| Param | Type | Description |
|-------|------|-------------|
| `sessionId` | string | MongoDB ObjectId |

**Request Body** _(none required)_

**Response `200`**
```json
{
  "success": true,
  "message": "AI insights generated.",
  "data": {
    "aiInsights": "The dataset contains several quality issues that may affect downstream analysis...",
    "rootCauses": ["Inconsistent data entry", "Missing ETL validation"],
    "riskAssessment": "High — 7 % of rows contain critical nulls in key join fields.",
    "priorityOrder": ["Fix missing email values", "Remove 3 duplicate rows", "Standardise date formats"]
  }
}
```

**Errors**
| Code | Reason |
|------|--------|
| 404  | Session not found |
| 502  | Gemini API error |

---

## Repair

### `POST /api/repair/:sessionId`

Apply one or more automated repair strategies to the session dataset.

**Path Parameters**
| Param | Type | Description |
|-------|------|-------------|
| `sessionId` | string | MongoDB ObjectId |

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

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `fixMissing` | boolean | `true` | Impute or drop rows with null/empty values |
| `removeDuplicates` | boolean | `true` | Deduplicate exact-match rows |
| `fixFormats` | boolean | `true` | Standardise date, phone, email formats |
| `fixOutliers` | boolean | `false` | Clip or remove statistical outliers |

**Response `200`**
```json
{
  "success": true,
  "message": "Data repaired successfully.",
  "data": {
    "repairedRowCount": 195,
    "repairCount": 12,
    "newQualityScore": 94,
    "remainingIssues": 2,
    "repairLog": [
      { "action": "imputed", "field": "email", "rowIndex": 3, "value": "N/A" },
      { "action": "removed_duplicate", "rowIndex": 7 }
    ],
    "aiExplanation": "12 repairs applied. Missing emails were imputed with 'N/A'. 3 duplicate rows removed."
  }
}
```

**Errors**
| Code | Reason |
|------|--------|
| 400  | Invalid repairOptions |
| 404  | Session not found |
| 500  | Repair processing error |

---

### `GET /api/repair/:sessionId/diff`

Retrieve a row-level diff between the original and repaired datasets.

**Path Parameters**
| Param | Type | Description |
|-------|------|-------------|
| `sessionId` | string | MongoDB ObjectId |

**Response `200`**
```json
{
  "success": true,
  "message": "Diff retrieved successfully.",
  "data": {
    "original": [ { "id": 1, "email": null, "age": 250 } ],
    "repaired": [ { "id": 1, "email": "N/A", "age": 45 } ],
    "changes": [
      { "rowIndex": 0, "field": "email", "original": null, "fixed": "N/A" },
      { "rowIndex": 0, "field": "age",   "original": 250,  "fixed": 45 }
    ],
    "totalChanges": 2
  }
}
```

**Errors**
| Code | Reason |
|------|--------|
| 404  | Session not found or no repairs run yet |

---

## Download

### `GET /api/download/:sessionId`

Download the repaired (or original) dataset as a file.

**Path Parameters**
| Param | Type | Description |
|-------|------|-------------|
| `sessionId` | string | MongoDB ObjectId |

**Query Parameters**
| Param | Values | Default | Description |
|-------|--------|---------|-------------|
| `format` | `csv` \| `xlsx` | `csv` | Output format |

**Response `200`** — Binary file download
- Content-Type: `text/csv` or `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
- Content-Disposition: `attachment; filename="datafix_repaired_<sessionId>.csv"`

**Errors**
| Code | Reason |
|------|--------|
| 400  | Unsupported format |
| 404  | Session not found |

---

## Report

### `GET /api/report/:sessionId`

Generate and return a comprehensive data quality report.

**Path Parameters**
| Param | Type | Description |
|-------|------|-------------|
| `sessionId` | string | MongoDB ObjectId |

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
      "uploadedAt": "2024-01-01T10:00:00.000Z",
      "analysedAt": "2024-01-01T10:00:02.000Z",
      "repairedAt": "2024-01-01T10:05:00.000Z"
    }
  }
}
```

**Errors**
| Code | Reason |
|------|--------|
| 404  | Session not found |

---

## Rate Limits

| Scope | Window | Limit |
|-------|--------|-------|
| All `/api/*` routes | 15 minutes | 200 requests |
| `/api/upload` | 10 minutes | 20 uploads |

---

## Session Lifecycle

```
POST /upload  →  GET /analysis/:id  →  POST /analysis/:id/ai-insights
                                     →  POST /repair/:id
                                            ↓
                               GET /repair/:id/diff
                               GET /download/:id
                               GET /report/:id
```
