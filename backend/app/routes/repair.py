from datetime import datetime, timezone
from fastapi import APIRouter, Body
from fastapi.responses import JSONResponse
from app.database import SessionStore
from app.services.repair_service import RepairService
from app.services.diff_service import DiffService
from app.models.schemas import RepairRequest

router = APIRouter()

@router.post('/repair/{session_id}')
def apply_repair(session_id: str, request_data: dict = Body(default={})):
    session = SessionStore.find_by_id(session_id)
    if not session:
        return JSONResponse(
            status_code=404,
            content={'success': False, 'message': 'Session not found.', 'errors': [{'field': 'sessionId', 'message': 'Session not found'}]}
        )

    repair_options = request_data.get('repairOptions', {
        'fixMissing': True,
        'removeDuplicates': True,
        'fixFormats': True,
        'fixOutliers': False
    })

    original_records = session.get('originalData', [])
    columns = session.get('columns', [])

    try:
        repaired_records, repair_log, new_quality_score, remaining_issues_count, ai_explanation = (
            RepairService.apply_repairs(original_records, columns, repair_options)
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={'success': False, 'message': f'Repair processing error: {str(e)}', 'errors': [{'message': str(e)}]}
        )

    now = datetime.now(timezone.utc).isoformat()
    SessionStore.update_by_id(session_id, {
        'repairedData': repaired_records,
        'repairs': repair_log,
        'qualityScore': new_quality_score,
        'status': 'repaired',
        'repairedAt': now,
        'updatedAt': now
    })

    return JSONResponse(
        status_code=200,
        content={
            'success': True,
            'message': 'Data repaired successfully.',
            'data': {
                'repairedRowCount': len(repaired_records),
                'repairCount': len(repair_log),
                'newQualityScore': new_quality_score,
                'remainingIssues': remaining_issues_count,
                'repairLog': repair_log,
                'aiExplanation': ai_explanation
            }
        }
    )

@router.get('/repair/{session_id}/diff')
def get_diff(session_id: str):
    session = SessionStore.find_by_id(session_id)
    if not session:
        return JSONResponse(
            status_code=404,
            content={'success': False, 'message': 'Session not found.', 'errors': [{'field': 'sessionId', 'message': 'Session not found'}]}
        )

    repaired_data = session.get('repairedData')
    if repaired_data is None:
        return JSONResponse(
            status_code=404,
            content={'success': False, 'message': 'No repairs run yet for this session.', 'errors': [{'message': 'Repairs not executed'}]}
        )

    original_data = session.get('originalData', [])
    columns = session.get('columns', [])

    diff_data = DiffService.calculate_diff(original_data, repaired_data, columns)

    return JSONResponse(
        status_code=200,
        content={
            'success': True,
            'message': 'Diff retrieved successfully.',
            'data': diff_data
        }
    )
