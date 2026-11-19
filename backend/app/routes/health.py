from datetime import datetime, timezone
from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get('/health')
def health_check():
    return JSONResponse(
        status_code=200,
        content={
            'success': True,
            'message': 'DataFix API is running.',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'version': '1.0.0'
        }
    )
