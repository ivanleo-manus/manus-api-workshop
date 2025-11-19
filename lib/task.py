"""
Task creation and polling utilities for Manus API.
"""

import time
import requests
from typing import Optional, Dict, Any, List, TypedDict, Union


__all__ = [
    "FileIDAttachment",
    "URLAttachment", 
    "Base64Attachment",
    "Attachment",
    "create_task",
    "get_task_status",
    "poll_task_until_complete",
    "extract_task_output_text"
]


class FileIDAttachment(TypedDict):
    """Attachment using a file_id from the Files API."""
    file_id: str
    filename: str


class URLAttachment(TypedDict):
    """Attachment using a public URL."""
    url: str
    filename: Optional[str]


class Base64Attachment(TypedDict):
    """Attachment using base64-encoded data."""
    file_data: str
    filename: str
    mime_type: Optional[str]


# Union type for all attachment types
Attachment = Union[FileIDAttachment, URLAttachment, Base64Attachment]


def create_task(
    api_key: str,
    prompt: str,
    agent_profile: str = "manus-1.5",
    base_url: str = "https://api.manus.ai/v1",
    task_mode: Optional[str] = None,
    attachments: Optional[List[Attachment]] = None,
    connectors: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Create a new Manus task.
    
    Args:
        api_key: The Manus API key
        prompt: The task prompt/instruction
        agent_profile: The agent profile to use (default: "manus-1.5")
                      Options: "manus-1.5", "manus-1.5-lite"
        base_url: The base URL for the Manus API
        task_mode: Optional task mode (e.g., "agent")
        attachments: Optional list of file attachments (FileIDAttachment, URLAttachment, or Base64Attachment)
        connectors: Optional list of connector IDs to enable for this task
        
    Returns:
        dict: The task response containing task_id, task_url, and task_title
        
    Raises:
        requests.exceptions.HTTPError: If the API request fails
    """
    headers = {
        "API_KEY": api_key,
        "Content-Type": "application/json"
    }
    
    data = {
        "prompt": prompt,
        "agentProfile": agent_profile
    }
    
    # Add optional parameters
    if task_mode:
        data["taskMode"] = task_mode
    if attachments:
        data["attachments"] = attachments
    if connectors:
        data["connectors"] = connectors
    
    response = requests.post(
        f"{base_url}/tasks",
        headers=headers,
        json=data
    )
    print(response.text)
    response.raise_for_status()

    
    return response.json()


def get_task_status(
    api_key: str,
    task_id: str,
    base_url: str = "https://api.manus.ai/v1"
) -> Dict[str, Any]:
    """
    Get the current status and details of a task.
    
    Args:
        api_key: The Manus API key
        task_id: The task ID to query
        base_url: The base URL for the Manus API
        
    Returns:
        dict: The full task object containing status, output, metadata, etc.
        
    Raises:
        requests.exceptions.HTTPError: If the API request fails
    """
    url = f"{base_url}/tasks/{task_id}"
    headers = {"API_KEY": api_key}
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    return response.json()


def poll_task_until_complete(
    api_key: str,
    task_id: str,
    base_url: str = "https://api.manus.ai/v1",
    polling_interval: int = 10,
    max_attempts: Optional[int] = None,
    verbose: bool = True
) -> Dict[str, Any]:
    """
    Poll a task until it completes (status != "running").
    
    Args:
        api_key: The Manus API key
        task_id: The task ID to poll
        base_url: The base URL for the Manus API
        polling_interval: Time in seconds between polling attempts (default: 10)
        max_attempts: Maximum number of polling attempts (None for unlimited)
        verbose: Whether to print status updates (default: True)
        
    Returns:
        dict: The final task object after completion
        
    Raises:
        requests.exceptions.HTTPError: If the API request fails
        TimeoutError: If max_attempts is reached before task completes
    """
    attempts = 0
    
    while True:
        task = get_task_status(api_key, task_id, base_url)
        status = task["status"]
        task_url = task.get("metadata", {}).get("task_url", "")
        
        # Check if task is no longer running
        if status != "running":
            if verbose:
                print(f"✓ Task {task_id} is now {status}")
            return task
        
        # Check max attempts
        attempts += 1
        if max_attempts and attempts >= max_attempts:
            raise TimeoutError(
                f"Task {task_id} did not complete after {max_attempts} attempts"
            )
        
        # Print status and wait
        if verbose:
            print(
                f"⏳ Task still running... (attempt {attempts}, "
                f"check progress at {task_url})"
            )
        
        time.sleep(polling_interval)


def extract_task_output_text(task: Dict[str, Any]) -> List[str]:
    """
    Extract all text outputs from a completed task.
    
    Args:
        task: The task object returned from get_task_status or poll_task_until_complete
        
    Returns:
        list: List of text content strings from the task output
    """
    outputs = []
    
    for item in task.get("output", []):
        if item.get("role") == "assistant":
            for content in item.get("content", []):
                if content.get("type") == "output_text":
                    outputs.append(content.get("text", ""))
    
    return outputs
