"""
Part 2: File Handling - Starter Template

In this exercise, you'll learn to:
1. Upload files to Manus
2. Attach files to tasks
3. Create tasks with file attachments
4. Retrieve task results with attachments

TODO: Complete the functions below.
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


def upload_file(file_path):
    """
    Upload a file to Manus and get a file ID.
    
    This is a two-step process:
    1. Create a file record to get an upload URL
    2. Upload the file content to that URL
    
    Args:
        file_path (str): Path to the file to upload
    
    Returns:
        str: The file ID
    
    TODO: Implement this function
    """
    filename = os.path.basename(file_path)
    
    # Step 1: Create file record
    # TODO: POST to /files with {"filename": filename}
    # This returns: {id, upload_url, status, ...}
    
    # Step 2: Upload file content
    # TODO: Read the file content
    # TODO: PUT the content to the upload_url
    
    # TODO: Return the file ID
    pass


def create_task_with_file(prompt, file_id, agent_profile="manus-1.5"):
    """
    Create a task with a file attachment.
    
    Args:
        prompt (str): The task instruction
        file_id (str): The ID of the uploaded file
        agent_profile (str): The agent profile to use
    
    Returns:
        dict: The task response
    
    TODO: Implement this function
    Hint: Include attachments array in the request body
    """
    headers = {
        "API_KEY": API_KEY,
        "Content-Type": "application/json"
    }
    
    # TODO: Create request body with attachments
    data = {
        "prompt": prompt,
        "agentProfile": agent_profile,
        # TODO: Add attachments array with file_id
    }
    
    # TODO: Make POST request to /tasks
    pass


def get_task_result(task_id):
    """
    Get the complete task result including any output attachments.
    
    Args:
        task_id (str): The task ID
    
    Returns:
        dict: The complete task details
    
    TODO: Implement this function
    """
    # TODO: GET /tasks/{task_id}
    pass


def wait_for_completion(task_id, check_interval=5, max_wait=300):
    """
    Poll until task completes.
    """
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        task = get_task_result(task_id)
        status = task.get("status")
        
        print(f"  Status: {status}")
        
        if status != "running":
            return task
        
        time.sleep(check_interval)
    
    raise TimeoutError(f"Task did not complete within {max_wait} seconds")


def main():
    """
    Main function demonstrating file handling workflow.
    """
    print("=" * 60)
    print("Part 2: File Handling")
    print("=" * 60)
    
    if not API_KEY:
        print("ERROR: MANUS_API_KEY not found")
        return
    
    # Step 1: Upload a file
    print("\n[Step 1] Uploading file...")
    file_path = "sample-document.txt"
    
    # Create sample file if it doesn't exist
    if not os.path.exists(file_path):
        with open(file_path, "w") as f:
            f.write("This is a sample document for the Manus API workshop.\n")
            f.write("It contains some text that the AI agent can analyze.\n")
            f.write("\nKey points:\n")
            f.write("- Manus API supports file uploads\n")
            f.write("- Files can be attached to tasks\n")
            f.write("- The agent can analyze document content\n")
    
    try:
        file_id = upload_file(file_path)
        print(f"✓ File uploaded successfully!")
        print(f"  File ID: {file_id}")
    except Exception as e:
        print(f"✗ Failed to upload file: {e}")
        return
    
    # Step 2: Create task with file
    print("\n[Step 2] Creating task with file attachment...")
    prompt = "Please analyze this document and summarize the key points."
    
    try:
        task = create_task_with_file(prompt, file_id)
        task_id = task.get("task_id")
        print(f"✓ Task created with file attachment!")
        print(f"  Task ID: {task_id}")
    except Exception as e:
        print(f"✗ Failed to create task: {e}")
        return
    
    # Step 3: Wait for completion
    print("\n[Step 3] Waiting for task to complete...")
    try:
        result = wait_for_completion(task_id)
        print(f"✓ Task completed!")
        print(f"  Status: {result.get('status')}")
        
        # Check for output attachments
        attachments = result.get("attachments", [])
        if attachments:
            print(f"  Output attachments: {len(attachments)}")
            for att in attachments:
                print(f"    - {att.get('filename')}")
    except Exception as e:
        print(f"✗ Error: {e}")
        return
    
    print("\n" + "=" * 60)
    print("Part 2 Complete! You've successfully:")
    print("  • Uploaded a file to Manus")
    print("  • Created a task with file attachment")
    print("  • Retrieved task results")
    print("=" * 60)


if __name__ == "__main__":
    main()
