"""
Configuration loader for MediVault application.
Reads from config.properties file.
"""
from pathlib import Path
from typing import Optional


class Config:
    """Application configuration loaded from config.properties"""
    
    def __init__(self, config_file: str = "config.properties"):
        """Initialize configuration from properties file"""
        # Get project root directory (parent of backend)
        project_root = Path(__file__).parent.parent.parent
        config_path = project_root / config_file
        
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        self._config = self._load_properties(config_path)
        self._load_config()
    
    def _load_properties(self, file_path: Path) -> dict:
        """Load properties from .properties file"""
        config = {}
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                
                # Split key and value
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    # Remove quotes if present
                    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
                        value = value[1:-1]
                    config[key] = value
        
        return config
    
    def _load_config(self):
        """Load all configuration values"""
        # Application
        self.APP_NAME = self._config.get('APP_NAME', 'MediVault')
        self.DEBUG = self._config.get('DEBUG', 'False').lower() == 'true'
        
        # Server
        self.HOST = self._config.get('HOST', '0.0.0.0')
        self.PORT = int(self._config.get('PORT', '8000'))
        
        # Frontend directory
        project_root = Path(__file__).parent.parent.parent
        frontend_dir = self._config.get('FRONTEND_DIR', 'frontend')
        self.FRONTEND_DIR = project_root / frontend_dir
        
        # Login credentials
        self.USERNAME = self._config.get('USERNAME', '')
        self.PASSWORD = self._config.get('PASSWORD', '')
        
        # Gemini configuration
        self.GEMINI_API_KEY = self._config.get('GEMINI_API_KEY', '')
        self.GEMINI_MODEL = self._config.get('GEMINI_MODEL', 'gemini-2.5-flash')
        
        # Medical records directory
        project_root = Path(__file__).parent.parent.parent
        medical_records_dir = self._config.get('MEDICAL_RECORDS_DIR', 'arpita_medical_reports')
        self.MEDICAL_RECORDS_DIR = project_root / medical_records_dir
        
        # RAG Configuration
        # Text chunking settings
        self.CHUNK_SIZE = int(self._config.get('CHUNK_SIZE', '500'))
        self.CHUNK_OVERLAP = int(self._config.get('CHUNK_OVERLAP', '50'))
        self.TOP_K_CHUNKS = int(self._config.get('TOP_K_CHUNKS', '3'))
        
        # Embedding model
        self.EMBEDDING_MODEL = self._config.get('EMBEDDING_MODEL', 'all-MiniLM-L6-v2')
        
        # Vector database path
        project_root = Path(__file__).parent.parent.parent
        vector_db_path = self._config.get('VECTOR_DB_PATH', 'vector_db')
        self.VECTOR_DB_PATH = project_root / vector_db_path
    
    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get configuration value by key"""
        return self._config.get(key, default)


# Global configuration instance
config = Config()
