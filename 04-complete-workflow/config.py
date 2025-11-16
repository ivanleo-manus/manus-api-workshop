"""
Configuration management for the workflow.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """
    Application configuration.
    """
    
    # Manus API
    MANUS_API_KEY = os.getenv("MANUS_API_KEY")
    MANUS_BASE_URL = "https://api.manus.ai/v1"
    
    # Webhook
    WEBHOOK_URL = os.getenv("WEBHOOK_URL")
    
    # Task defaults
    DEFAULT_AGENT_PROFILE = "manus-1.5"
    DEFAULT_TIMEOUT = 300  # seconds
    DEFAULT_POLL_INTERVAL = 5  # seconds
    
    # File handling
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB
    ALLOWED_FILE_TYPES = [
        '.txt', '.pdf', '.docx', '.csv',
        '.xlsx', '.md', '.json', '.xml'
    ]
    
    # Retry configuration
    MAX_RETRIES = 3
    RETRY_DELAY = 2  # seconds
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def validate(cls):
        """
        Validate required configuration.
        """
        if not cls.MANUS_API_KEY:
            raise ValueError("MANUS_API_KEY is required")
        
        return True


if __name__ == "__main__":
    # Test configuration
    try:
        Config.validate()
        print("✓ Configuration valid")
        print(f"  API Key: {'*' * 20}{Config.MANUS_API_KEY[-8:]}")
        print(f"  Base URL: {Config.MANUS_BASE_URL}")
        print(f"  Webhook URL: {Config.WEBHOOK_URL or 'Not configured'}")
    except ValueError as e:
        print(f"✗ Configuration error: {e}")
