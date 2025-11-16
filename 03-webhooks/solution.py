"""
Part 3: Webhooks - Complete Solution

This solution demonstrates:
1. Registering a webhook endpoint
2. Creating tasks that trigger webhooks
3. Handling webhook events
4. Deleting webhooks

Run webhook-handler.py in a separate terminal first!
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
API_KEY = os.getenv("MANUS_API_KEY")
BASE_URL = "https://api.manus.ai/v1"


def register_webhook(webhook_url):
    """
    Register a webhook endpoint with Manus.
    
    Args:
        webhook_url (str): The publicly accessible URL for webhooks
    
    Returns:
        dict: The webhook registration response
    """
    headers = {
        "API_KEY": API_KEY,
        "Content-Type": "application/json"
    }
    
    data = {
        "url": webhook_url
    }
    
    response = requests.post(
        f"{BASE_URL}/webhooks",
        headers=headers,
        json=data
    )
    response.raise_for_status()
    
    return response.json()


def create_task(prompt, agent_profile="manus-1.5"):
    """
    Create a task that will trigger webhook events.
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


def delete_webhook(webhook_id):
    """
    Delete a registered webhook.
    
    Args:
        webhook_id (str): The webhook ID to delete
    """
    headers = {
        "API_KEY": API_KEY
    }
    
    response = requests.delete(
        f"{BASE_URL}/webhooks/{webhook_id}",
        headers=headers
    )
    response.raise_for_status()
    
    return response.status_code == 200


def main():
    """
    Main function demonstrating webhook workflow.
    """
    print("=" * 60)
    print("Part 3: Webhooks")
    print("=" * 60)
    
    if not API_KEY:
        print("ERROR: MANUS_API_KEY not found")
        return
    
    # Get webhook URL from user
    print("\nBefore registering a webhook, you need a publicly accessible URL.")
    print("\nOptions:")
    print("  1. Use webhook.site (easiest for testing)")
    print("  2. Run webhook-handler.py and expose with ngrok")
    print("  3. Deploy webhook-handler.py to a server")
    
    webhook_url = input("\nEnter your webhook URL: ").strip()
    
    if not webhook_url:
        print("No webhook URL provided. Using webhook.site example...")
        print("\nVisit https://webhook.site to get a unique URL")
        return
    
    # Step 1: Register webhook
    print(f"\n[Step 1] Registering webhook...")
    print(f"  URL: {webhook_url}")
    
    try:
        webhook = register_webhook(webhook_url)
        webhook_id = webhook.get("webhook_id")
        print(f"✓ Webhook registered successfully!")
        print(f"  Webhook ID: {webhook_id}")
    except Exception as e:
        print(f"✗ Failed to register webhook: {e}")
        return
    
    # Step 2: Create a task (will trigger webhook events)
    print("\n[Step 2] Creating a task...")
    prompt = "What are the three primary colors? Provide a brief answer."
    
    try:
        task = create_task(prompt)
        task_id = task.get("task_id")
        print(f"✓ Task created!")
        print(f"  Task ID: {task_id}")
        print(f"\nThis task will trigger two webhook events:")
        print(f"  1. task_created - Sent immediately")
        print(f"  2. task_stopped - Sent when task completes")
    except Exception as e:
        print(f"✗ Failed to create task: {e}")
        return
    
    # Step 3: Wait for webhooks
    print("\n[Step 3] Waiting for webhook events...")
    print(f"\nCheck your webhook endpoint for incoming events:")
    print(f"  {webhook_url}")
    
    if "webhook.site" in webhook_url:
        print(f"\nVisit: {webhook_url}")
    else:
        print(f"\nIf using webhook-handler.py, check the terminal output")
        print(f"Or visit: http://localhost:5000/events")
    
    input("\nPress Enter once you've seen the webhook events...")
    
    # Step 4: Clean up (optional)
    print("\n[Step 4] Cleaning up...")
    cleanup = input("Delete the webhook? (y/n): ").strip().lower()
    
    if cleanup == 'y':
        try:
            delete_webhook(webhook_id)
            print(f"✓ Webhook deleted")
        except Exception as e:
            print(f"✗ Failed to delete webhook: {e}")
    else:
        print(f"Webhook remains active: {webhook_id}")
        print(f"Delete it later with: DELETE /webhooks/{webhook_id}")
    
    print("\n" + "=" * 60)
    print("Part 3 Complete! You've successfully:")
    print("  • Registered a webhook endpoint")
    print("  • Created a task that triggers webhooks")
    print("  • Received webhook events")
    print("  • Understood event-driven architecture")
    print("=" * 60)
    
    print("\nKey Takeaways:")
    print("  • Webhooks eliminate the need for polling")
    print("  • You get real-time notifications")
    print("  • Production systems should use webhooks")
    print("  • Handle both task_created and task_stopped events")


if __name__ == "__main__":
    main()
