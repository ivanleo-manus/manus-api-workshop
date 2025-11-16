"""
Part 1: Manus API Basics - Starter Template

In this exercise, you'll learn to:
1. Set up authentication with the Manus API
2. Create your first task
3. Check task status
4. Retrieve task results

TODO: Complete the functions below by following the instructions.
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
        agent_profile (str): The agent profile to use (manus-1.5 or manus-1.5-lite)
    
    Returns:
        dict: The task response containing task_id, task_url, etc.
    
    TODO: Implement this function
    Hint: Use POST request to /tasks endpoint with proper headers
    """
    # TODO: Set up headers with API_KEY
    headers = {
        # Add your headers here
    }
    
    # TODO: Create the request body
    data = {
        # Add your data here
    }
    
    # TODO: Make the POST request
    # response = requests.post(...)
    
    # TODO: Return the JSON response
    pass


def get_task_status(task_id):
    """
    Get the current status of a task.
    
    Args:
        task_id (str): The ID of the task to check
    
    Returns:
        dict: The task details including status
    
    TODO: Implement this function
    Hint: Use GET request to /tasks/{task_id} endpoint
    """
    # TODO: Set up headers
    headers = {
        # Add your headers here
    }
    
    # TODO: Make the GET request
    # response = requests.get(...)
    
    # TODO: Return the JSON response
    pass


def wait_for_completion(task_id, check_interval=5, max_wait=300):
    """
    Poll the task status until it's no longer running.
    
    Args:
        task_id (str): The ID of the task to monitor
        check_interval (int): Seconds between status checks
        max_wait (int): Maximum seconds to wait
    
    Returns:
        dict: The final task details
    
    TODO: Implement this function
    Hint: Use a loop to repeatedly check status until it's not "running"
    """
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        # TODO: Get the current task status
        
        # TODO: Check if status is not "running"
        # If so, return the task details
        
        # TODO: Print status update
        
        # TODO: Wait before checking again
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
