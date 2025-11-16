"""
Part 1: Manus API Basics - Complete Solution

This solution demonstrates:
1. Authentication with the Manus API
2. Creating tasks
3. Checking task status
4. Polling for completion
"""

import os
import time
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
API_KEY = os.getenv("MANUS_API_KEY")
BASE_URL = "https://api.manus.ai/v1"


def create_task(prompt, agent_profile="manus-1.5"):
    """
    Create a new task with the Manus API.
    
    Args:
        prompt (str): The instruction for the AI agent
        agent_profile (str): The agent profile to use
    
    Returns:
        dict: The task response containing task_id, task_url, etc.
    """
    headers = {
        "API_KEY": API_KEY,
        "Content-Type": "application/json"
    }
    
    data = {
        "prompt": prompt,
        "agentProfile": agent_profile
    }
    
    response = requests.post(
        f"{BASE_URL}/tasks",
        headers=headers,
        json=data
    )
    response.raise_for_status()
    
    return response.json()


def get_task_status(task_id):
    """
    Get the current status of a task.
    
    Args:
        task_id (str): The ID of the task to check
    
    Returns:
        dict: The task details including status
    """
    headers = {
        "API_KEY": API_KEY
    }
    
    response = requests.get(
        f"{BASE_URL}/tasks/{task_id}",
        headers=headers
    )
    response.raise_for_status()
    
    return response.json()


def wait_for_completion(task_id, check_interval=5, max_wait=300):
    """
    Poll the task status until it's no longer running.
    
    Args:
        task_id (str): The ID of the task to monitor
        check_interval (int): Seconds between status checks
        max_wait (int): Maximum seconds to wait
    
    Returns:
        dict: The final task details
    """
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        task = get_task_status(task_id)
        status = task.get("status")
        
        print(f"  Status: {status} (checked at {time.strftime('%H:%M:%S')})")
        
        if status != "running":
            return task
        
        time.sleep(check_interval)
    
    raise TimeoutError(f"Task {task_id} did not complete within {max_wait} seconds")


def main():
    """
    Main function to demonstrate the workflow.
    """
    print("=" * 60)
    print("Part 1: Manus API Basics")
    print("=" * 60)
    
    # Check if API key is set
    if not API_KEY:
        print("ERROR: MANUS_API_KEY not found in environment variables")
        print("Please create a .env file with your API key")
        return
    
    # Step 1: Create a task
    print("\n[Step 1] Creating a task...")
    prompt = "What is the capital of France? Please provide a brief answer."
    
    try:
        task = create_task(prompt)
        task_id = task.get("task_id")
        print(f"✓ Task created successfully!")
        print(f"  Task ID: {task_id}")
        print(f"  Task URL: {task.get('task_url')}")
    except Exception as e:
        print(f"✗ Failed to create task: {e}")
        return
    
    # Step 2: Check initial status
    print("\n[Step 2] Checking task status...")
    try:
        status = get_task_status(task_id)
        print(f"✓ Current status: {status.get('status')}")
    except Exception as e:
        print(f"✗ Failed to get status: {e}")
        return
    
    # Step 3: Wait for completion
    print("\n[Step 3] Waiting for task to complete...")
    try:
        final_task = wait_for_completion(task_id)
        print(f"✓ Task completed!")
        print(f"  Final status: {final_task.get('status')}")
    except Exception as e:
        print(f"✗ Error waiting for completion: {e}")
        return
    
    print("\n" + "=" * 60)
    print("Part 1 Complete! You've successfully:")
    print("  • Created a task via the API")
    print("  • Checked task status")
    print("  • Waited for task completion")
    print("=" * 60)


if __name__ == "__main__":
    main()
