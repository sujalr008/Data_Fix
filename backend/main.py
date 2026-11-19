import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

from app.config import PORT, FRONTEND_URL
from app.database import init_db
from app.routes.health import router as health_router
from app.routes.upload import router as upload_router
from app.routes.analysis import router as analysis_router
from app.routes.repair import router as repair_router
from app.routes.download import router as download_router
from app.routes.report import router as report_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Connect database
    init_db()
    yield
    # Shutdown

app = FastAPI(
    title='DataFix – Autonomous Data Quality and Repair Engine API',
    description='Backend API for automated data cleaning, validation, repair, and reporting.',
    version='1.0.0',
    lifespan=lifespan
)

# CORS configuration
allowed_origins = [
    'http://localhost:5173',
    'http://localhost:3000',
    'http://127.0.0.1:5173',
    'http://127.0.0.1:3000',
]
if FRONTEND_URL and FRONTEND_URL not in allowed_origins:
    allowed_origins.append(FRONTEND_URL)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],  # Allow all for hackathon flexibility & seamless frontend connection
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
    expose_headers=['Content-Disposition']
)

# Global validation error handler matching API_CONTRACTS.md
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        loc = err.get('loc', [])
        field_name = loc[-1] if loc else 'body'
        errors.append({'field': str(field_name), 'message': err.get('msg', 'Validation error')})
    return JSONResponse(
        status_code=422,
        content={
            'success': False,
            'message': 'Validation failed.',
            'errors': errors
        }
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            'success': False,
            'message': f'Internal server error: {str(exc)}',
            'errors': [{'message': str(exc)}]
        }
    )

# Mount all API routers with prefix /api
app.include_router(health_router, prefix='/api', tags=['Health'])
app.include_router(upload_router, prefix='/api', tags=['Upload'])
app.include_router(analysis_router, prefix='/api', tags=['Analysis'])
app.include_router(repair_router, prefix='/api', tags=['Repair'])
app.include_router(download_router, prefix='/api', tags=['Download'])
app.include_router(report_router, prefix='/api', tags=['Report'])

if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=PORT, reload=False)
