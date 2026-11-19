import logging
import certifi
from bson import ObjectId
from pymongo import MongoClient
from app.config import MONGODB_URI

logger = logging.getLogger('datafix.db')

client = None
db = None
_memory_sessions = {}

def init_db():
    global client, db
    try:
        client = MongoClient(
            MONGODB_URI,
            tlsCAFile=certifi.where(),
            tlsAllowInvalidCertificates=True,
            serverSelectionTimeoutMS=3000
        )
        # Test connection
        client.admin.command('ping')
        db = client.get_default_database()
        if db is None:
            db = client['datafix']
        logger.info('Connected to MongoDB successfully.')
    except Exception as e:
        logger.warning(f'MongoDB connection warning: {e}. Active in-memory fallback enabled for resilience.')
        db = None

def get_db():
    return db

class SessionStore:
    @staticmethod
    def create(data: dict) -> str:
        data = dict(data)
        if '_id' not in data:
            data['_id'] = ObjectId()
        session_id = str(data['_id'])
        
        # In-memory store
        _memory_sessions[session_id] = {**data, '_id': session_id}
        
        # Persist to Mongo if available
        if db is not None:
            try:
                db.sessions.insert_one(data)
            except Exception as e:
                logger.warning(f'Mongo insert failed: {e}. Using in-memory fallback.')
        return session_id

    @staticmethod
    def find_by_id(session_id: str) -> dict | None:
        # Check Mongo first if connected
        if db is not None:
            try:
                # Try ObjectId first
                try:
                    obj_id = ObjectId(session_id)
                    doc = db.sessions.find_one({'_id': obj_id})
                except Exception:
                    doc = db.sessions.find_one({'_id': session_id})
                if doc:
                    doc['sessionId'] = str(doc['_id'])
                    doc['_id'] = str(doc['_id'])
                    return doc
            except Exception as e:
                logger.warning(f'Mongo query failed: {e}. Checking in-memory store.')
                
        # Check in-memory store
        doc = _memory_sessions.get(str(session_id))
        if doc:
            doc['sessionId'] = str(doc['_id'])
            return doc
        return None

    @staticmethod
    def update_by_id(session_id: str, updates: dict) -> bool:
        # Update in-memory
        str_id = str(session_id)
        if str_id in _memory_sessions:
            _memory_sessions[str_id].update(updates)
            
        if db is not None:
            try:
                try:
                    obj_id = ObjectId(session_id)
                    db.sessions.update_one({'_id': obj_id}, {'': updates})
                except Exception:
                    db.sessions.update_one({'_id': session_id}, {'': updates})
                return True
            except Exception as e:
                logger.warning(f'Mongo update failed: {e}')
                return str_id in _memory_sessions
        return str_id in _memory_sessions
