import modal
import os
import requests

# Define our Modal app and image
app = modal.App("manus-webhook-receiver")
image = modal.Image.debian_slim().pip_install("fastapi[standard]", "requests")

# Define the secret we created
manus_secret = modal.Secret.from_name("manus-api-key")

@app.function(image=image, secrets=[manus_secret])
@modal.fastapi_endpoint(method="POST")
def handle_webhook(payload: dict):
    """
    Receives webhook events, and if a task has stopped, fetches its full details.
    """
    event_type = payload.get("event_type")
    print(f"🔔 Received event: {event_type}")

    # Check if the task has finished
    if event_type == "task_stopped":
        task_detail = payload.get("task_detail", {})
        task_id = task_detail.get("task_id")

        if task_id:
            print(f"✅ Task {task_id} stopped. Fetching full details...")
            
            # Fetch the full task object from the Manus API
            api_key = os.environ["MANUS_API_KEY"]
            base_url = "https://api.manus.ai/v1"
            
            response = requests.get(
                f"{base_url}/tasks/{task_id}",
                headers={"API_KEY": api_key}
            )
            
            if response.status_code == 200:
                full_task_details = response.json()
                print("🔍 Full task details:")
                print(full_task_details)
            else:
                print(f"❌ Error fetching task details: {response.status_code}")

    return {"status": "received"}