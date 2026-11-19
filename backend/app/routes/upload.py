from datetime import datetime, timezone
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from app.config import MAX_UPLOAD_SIZE
from app.services.parser_service import ParserService
from app.services.quality_service import DataQualityService
from app.database import SessionStore

router = APIRouter()

@router.post('/upload')
async def upload_file(file: UploadFile = File(...)):
    if not file or not file.filename:
        return JSONResponse(
            status_code=400,
            content={'success': False, 'message': 'No file provided.', 'errors': [{'field': 'file', 'message': 'No file provided'}]}
        )

    ext = file.filename.lower().split('.')[-1]
    if ext not in ['csv', 'xlsx', 'xls']:
        return JSONResponse(
            status_code=400,
            content={'success': False, 'message': 'Unsupported file type. Please upload a CSV or XLSX file.', 'errors': [{'field': 'file', 'message': 'Unsupported file type'}]}
        )

    content = await file.read()
    if len(content) > MAX_UPLOAD_SIZE:
        return JSONResponse(
            status_code=413,
            content={'success': False, 'message': 'File exceeds 10 MB limit.', 'errors': [{'field': 'file', 'message': 'File too large'}]}
        )

    try:
        records, columns, file_type = ParserService.parse_file(content, file.filename)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={'success': False, 'message': f'Parse error: {str(e)}', 'errors': [{'field': 'file', 'message': str(e)}]}
        )

    quality_score, issues = DataQualityService.analyze(records, columns)
    now = datetime.now(timezone.utc).isoformat()

    session_doc = {
        'originalData': records,
        'repairedData': None,
        'columns': columns,
        'rowCount': len(records),
        'columnCount': len(columns),
        'fileType': file_type,
        'qualityScore': quality_score,
        'issues': issues,
        'repairs': [],
        'aiInsights': None,
        'status': 'analysed',
        'createdAt': now,
        'updatedAt': now
    }

    try:
        session_id = SessionStore.create(session_doc)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={'success': False, 'message': f'Database error: {str(e)}', 'errors': [{'message': str(e)}]}
        )

    return JSONResponse(
        status_code=200,
        content={
            'success': True,
            'message': 'File uploaded and analysed successfully.',
            'data': {
                'sessionId': session_id,
                'qualityScore': quality_score,
                'issueCount': len(issues),
                'issues': issues,
                'columns': columns,
                'rowCount': len(records),
                'columnCount': len(columns),
                'fileType': file_type,
                'status': 'analysed'
            }
        }
    )
