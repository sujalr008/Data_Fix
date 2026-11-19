from datetime import datetime, timezone
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from app.database import SessionStore
from app.services.ai_service import AIService

router = APIRouter()

@router.get('/analysis/{session_id}')
def get_analysis(session_id: str):
    session = SessionStore.find_by_id(session_id)
    if not session:
        return JSONResponse(
            status_code=404,
            content={'success': False, 'message': 'Session not found.', 'errors': [{'field': 'sessionId', 'message': 'Session not found'}]}
        )

    return JSONResponse(
        status_code=200,
        content={
            'success': True,
            'message': 'Analysis retrieved successfully.',
            'data': {
                'sessionId': str(session.get('sessionId', session_id)),
                'qualityScore': session.get('qualityScore', 100),
                'issues': session.get('issues', []),
                'columns': session.get('columns', []),
                'aiInsights': session.get('aiInsights'),
                'repairs': session.get('repairs', []),
                'rowCount': session.get('rowCount', 0),
                'columnCount': session.get('columnCount', 0),
                'status': session.get('status', 'analysed')
            }
        }
    )

@router.post('/analysis/{session_id}/ai-insights')
def generate_ai_insights(session_id: str):
    session = SessionStore.find_by_id(session_id)
    if not session:
        return JSONResponse(
            status_code=404,
            content={'success': False, 'message': 'Session not found.', 'errors': [{'field': 'sessionId', 'message': 'Session not found'}]}
        )

    issues = session.get('issues', [])
    row_count = session.get('rowCount', 0)
    columns = session.get('columns', [])

    try:
        insights = AIService.generate_insights(issues, row_count, columns)
        SessionStore.update_by_id(session_id, {
            'aiInsights': insights.get('aiInsights'),
            'updatedAt': datetime.now(timezone.utc).isoformat()
        })
    except Exception as e:
        return JSONResponse(
            status_code=502,
            content={'success': False, 'message': f'AI generation error: {str(e)}', 'errors': [{'message': str(e)}]}
        )

    return JSONResponse(
        status_code=200,
        content={
            'success': True,
            'message': 'AI insights generated.',
            'data': insights
        }
    )
