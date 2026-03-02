"""
Firebase configuration and initialization.
Firebase is CRITICAL for state management and real-time data streaming.
"""
import os
import logging
from typing import Optional
from dataclasses import dataclass
from firebase_admin import credentials, firestore, initialize_app, App

logger = logging.getLogger(__name__)

@dataclass
class FirebaseConfig:
    """Firebase configuration data class"""
    project_id: str
    service_account_path: str = "serviceAccountKey.json"
    database_url: Optional[str] = None
    
    def validate(self) -> bool:
        """Validate Firebase configuration"""
        if not os.path.exists(self.service_account_path):
            logger.error(f"Service account file not found: {self.service_account_path}")
            return False
        return True

class FirebaseManager:
    """Manages Firebase initialization and provides Firestore access"""
    
    _app: Optional[App] = None
    _db: Optional[firestore.Client] = None
    
    def __init__(self, config: FirebaseConfig):
        self.config = config
        self._initialized = False
        
    def initialize(self) -> bool:
        """Initialize Firebase with error handling"""
        try:
            if not self.config.validate():
                return False
                
            # Load credentials
            cred = credentials.Certificate(self.config.service_account_path)
            
            # Initialize Firebase app
            init_kwargs = {
                'credential': cred,
                'project_id': self.config.project_id
            }
            
            if self.config.database_url:
                init_kwargs['databaseURL'] = self.config.database_url
                
            self._app = initialize_app(**init_kwargs)
            self._db = firestore.client()
            
            # Test connection
            test_ref = self._db.collection('system').document('connection_test')
            test_ref.set({'timestamp': firestore.SERVER_TIMESTAMP}, merge=True)
            
            self._initialized = True
            logger.info(f"Firebase initialized successfully for project: {self.config.project_id}")
            return True
            
        except Exception as e:
            logger.error(f"Firebase initialization failed: {str(e)}")
            # Fallback to local storage if Firebase fails
            logger.warning("Falling back to local state management")
            return False
    
    @property
    def db(self) -> firestore.Client:
        """Get Firestore client with lazy initialization"""
        if not self._initialized or self._db is None:
            raise RuntimeError("Firebase not initialized. Call initialize() first.")
        return self._db
    
    @property
    def app(self) -> App:
        """Get Firebase app instance"""
        if not self._initialized or self._app is None:
            raise RuntimeError("Firebase not initialized. Call initialize() first.")
        return self._app
    
    def get_collection(self, collection_name: str):
        """Safe collection access with validation"""
        if not collection_name or not isinstance(collection_name, str):
            raise ValueError("Collection name must be a non-empty string")
        return self.db.collection(collection_name)