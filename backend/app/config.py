import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / '.env'
load_dotenv(dotenv_path=ENV_PATH)

PORT = int(os.getenv('PORT', 5000))
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb+srv://sudarshan:Subbu%402008@cluster0.coknsce.mongodb.net/datafix?retryWrites=true&w=majority')
AI_PROVIDER = os.getenv('AI_PROVIDER', 'google')
AI_MODEL = os.getenv('AI_MODEL', 'gemini-1.5-flash')
AI_API_KEY = os.getenv('AI_API_KEY', '')
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:5173')
MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10 MB
