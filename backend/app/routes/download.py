from fastapi import APIRouter, Query, Response
from fastapi.responses import JSONResponse
from app.database import SessionStore
from app.services.parser_service import ParserService

router = APIRouter()

@router.get('/download/{session_id}')
def download_file(session_id: str, format: str = Query('csv', pattern='^(csv|xlsx)$')):
    session = SessionStore.find_by_id(session_id)
    if not session:
        return JSONResponse(
            status_code=404,
            content={'success': False, 'message': 'Session not found.', 'errors': [{'field': 'sessionId', 'message': 'Session not found'}]}
        )

    records = session.get('repairedData') or session.get('originalData', [])
    columns = session.get('columns', [])

    if format == 'csv':
        content = ParserService.export_csv(records, columns)
        media_type = 'text/csv'
        filename = f'datafix_repaired_{session_id}.csv'
    elif format == 'xlsx':
        content = ParserService.export_xlsx(records, columns)
        media_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        filename = f'datafix_repaired_{session_id}.xlsx'
    else:
        return JSONResponse(
            status_code=400,
            content={'success': False, 'message': 'Unsupported format. Use csv or xlsx.', 'errors': [{'field': 'format', 'message': 'Invalid format'}]}
        )

    return Response(
        content=content,
        media_type=media_type,
        headers={
            'Content-Disposition': f'attachment; filename=\"{filename}\"',
            'Access-Control-Expose-Headers': 'Content-Disposition'
        }
    )
