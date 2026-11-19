from fastapi import APIRouter
from fastapi.responses import JSONResponse
from app.database import SessionStore
from app.services.report_service import ReportService

router = APIRouter()

@router.get('/report/{session_id}')
def get_report(session_id: str):
    session = SessionStore.find_by_id(session_id)
    if not session:
        return JSONResponse(
            status_code=404,
            content={'success': False, 'message': 'Session not found.', 'errors': [{'field': 'sessionId', 'message': 'Session not found'}]}
        )

    try:
        report_data = ReportService.generate_report(session)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={'success': False, 'message': f'Report generation failed: {str(e)}', 'errors': [{'message': str(e)}]}
        )

    return JSONResponse(
        status_code=200,
        content={
            'success': True,
            'message': 'Report generated successfully.',
            'data': report_data
        }
    )
