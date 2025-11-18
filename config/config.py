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
    WB_API_URL = os.getenv('WB_API_URL', 'https://statistics-api.wildberries.ru')
    
    # Date filters
    DATE_FROM = os.getenv('DATE_FROM', '2025-10-13')
    DATE_TO = os.getenv('DATE_TO', '2025-10-19')
    
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
    
    @classmethod
    def print_config(cls):
        """Вывести текущую конфигурацию."""
        print("\n⚙️  КОНФИГУРАЦИЯ:")
        print("=" * 50)
        print(f"API URL: {cls.WB_API_URL}")
        print(f"API Key: {'*' * 20 if cls.WB_API_KEY else 'НЕ УКАЗАН'}")
        print(f"Период: {cls.DATE_FROM} - {cls.DATE_TO}")
        print(f"Выходная папка: {cls.OUTPUT_DIR}")
        print(f"Формат экспорта: {cls.EXPORT_FORMAT}")
        print("=" * 50)