"""
Environment configuration and API key validation for Manus API.
"""

import os
import requests
from dotenv import load_dotenv


def get_env_key():
    """
    Load and validate the Manus API key from environment variables.
    
    This function:
    1. Loads environment variables from .env file
    2. Retrieves the MANUS_API_KEY
    3. Validates the key by making a test request to the files endpoint
    
    Returns:
        str: The validated Manus API key
        
    Raises:
        ValueError: If the API key is not set or invalid
    """
    # Load API key from .env file
    load_dotenv()
    
    # Get the API key
    api_key = os.getenv("MANUS_API_KEY")
    
    # Validate API key is loaded
    if not api_key:
        raise ValueError("⚠️  Please set your MANUS_API_KEY in the .env file at the repository root")
    
    # Test the API key with the files endpoint
    try:
        url = "https://api.manus.ai/v1/files"
        response = requests.get(url, headers={"API_KEY": api_key})
        response.raise_for_status()
        
        # If we get here, the API key is valid
        return api_key
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            raise ValueError("⚠️  Invalid API key. Please check your MANUS_API_KEY in the .env file")
        else:
            raise ValueError(f"⚠️  API key validation failed: {str(e)}")
    except Exception as e:
        raise ValueError(f"⚠️  Failed to validate API key: {str(e)}")


def get_base_url():
    """
    Get the base URL for the Manus API.
    
    Returns:
        str: The base URL for the Manus API
    """
    return "https://api.manus.ai/v1"
