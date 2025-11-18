"""Configuration management."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration."""
    
    # WB API settings
    WB_API_KEY = os.getenv('WB_API_KEY', '')
    WB_API_URL = os.getenv('WB_API_URL', 'https://suppliers-api.wildberries.ru')
    
    # Date filters
    DATE_FROM = os.getenv('DATE_FROM', '2024-01-01')
    DATE_TO = os.getenv('DATE_TO', '2024-12-31')
    
    # Export settings
    OUTPUT_DIR = Path(os.getenv('OUTPUT_DIR', 'output'))
    EXPORT_FORMAT = os.getenv('EXPORT_FORMAT', 'json')
    
    @classmethod
    def validate(cls):
        """Validate configuration."""
        if not cls.WB_API_KEY:
            raise ValueError("Не указан WB_API_KEY в .env файле")
        return True
    
    @classmethod
    def ensure_output_dir(cls):
        """Create output directory if it doesn't exist."""
        cls.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)