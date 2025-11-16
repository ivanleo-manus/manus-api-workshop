"""
Part 4: Complete Workflow - Production-Ready Example

This demonstrates a complete, production-ready workflow:
1. Upload document
2. Create analysis task with webhook
3. Receive webhook notification
4. Download results
5. Send notification

This is a reference implementation showing best practices.
"""

import os
import time
import requests
from datetime import datetime
from dotenv import load_dotenv
from config import Config

# Load environment variables
load_dotenv()


class ManusWorkflow:
    """
    A production-ready workflow manager for Manus API.
    """
    
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("MANUS_API_KEY")
        self.base_url = "https://api.manus.ai/v1"
        self.session = requests.Session()
        self.session.headers.update({
            "API_KEY": self.api_key,
            "Content-Type": "application/json"
        })
    
    def upload_file(self, file_path):
        """
        Upload a file using the two-step process.
        
        Returns:
            str: File ID
        """
        filename = os.path.basename(file_path)
        
        # Step 1: Create file record
        response = self.session.post(
            f"{self.base_url}/files",
            json={"filename": filename}
        )
        response.raise_for_status()
        file_record = response.json()
        
        # Step 2: Upload content
        with open(file_path, "rb") as f:
            upload_response = requests.put(
                file_record["upload_url"],
                data=f.read()
            )
            upload_response.raise_for_status()
        
        return file_record["id"]
    
    def create_task(self, prompt, file_id=None, agent_profile="manus-1.5"):
        """
        Create a task with optional file attachment.
        
        Returns:
            dict: Task details
        """
        data = {
            "prompt": prompt,
            "agentProfile": agent_profile
        }
        
        if file_id:
            data["attachments"] = [{"file_id": file_id}]
        
        response = self.session.post(
            f"{self.base_url}/tasks",
            json=data
        )
        response.raise_for_status()
        
        return response.json()
    
    def get_task(self, task_id):
        """
        Get task details.
        
        Returns:
            dict: Task details
        """
        response = self.session.get(f"{self.base_url}/tasks/{task_id}")
        response.raise_for_status()
        return response.json()
    
    def register_webhook(self, webhook_url):
        """
        Register a webhook endpoint.
        
        Returns:
            dict: Webhook registration details
        """
        response = self.session.post(
            f"{self.base_url}/webhooks",
            json={"url": webhook_url}
        )
        response.raise_for_status()
        return response.json()
    
    def delete_webhook(self, webhook_id):
        """
        Delete a webhook.
        """
        response = self.session.delete(f"{self.base_url}/webhooks/{webhook_id}")
        response.raise_for_status()
        return True
    
    def wait_for_completion(self, task_id, timeout=300, interval=5):
        """
        Fallback polling method if webhooks aren't available.
        
        Returns:
            dict: Completed task details
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            task = self.get_task(task_id)
            status = task.get("status")
            
            if status != "running":
                return task
            
            time.sleep(interval)
        
        raise TimeoutError(f"Task {task_id} did not complete within {timeout}s")


def run_document_analysis_workflow():
    """
    Example workflow: Document analysis with webhook notifications.
    """
    print("=" * 70)
    print("Complete Workflow: Document Analysis with Webhooks")
    print("=" * 70)
    
    # Initialize workflow manager
    workflow = ManusWorkflow()
    
    # Step 1: Prepare document
    print("\n[Step 1] Preparing document...")
    doc_path = "analysis-document.txt"
    
    if not os.path.exists(doc_path):
        with open(doc_path, "w") as f:
            f.write("# Quarterly Business Report\n\n")
            f.write("## Revenue\n")
            f.write("Q4 revenue increased by 23% compared to Q3.\n\n")
            f.write("## Expenses\n")
            f.write("Operating expenses decreased by 8%.\n\n")
            f.write("## Key Metrics\n")
            f.write("- Customer acquisition: +15%\n")
            f.write("- Retention rate: 94%\n")
            f.write("- Net profit margin: 18%\n")
    
    print(f"✓ Document ready: {doc_path}")
    
    # Step 2: Upload document
    print("\n[Step 2] Uploading document...")
    try:
        file_id = workflow.upload_file(doc_path)
        print(f"✓ File uploaded: {file_id}")
    except Exception as e:
        print(f"✗ Upload failed: {e}")
        return
    
    # Step 3: Register webhook (optional)
    webhook_url = os.getenv("WEBHOOK_URL")
    webhook_id = None
    
    if webhook_url:
        print(f"\n[Step 3] Registering webhook...")
        print(f"  URL: {webhook_url}")
        try:
            webhook = workflow.register_webhook(webhook_url)
            webhook_id = webhook.get("webhook_id")
            print(f"✓ Webhook registered: {webhook_id}")
        except Exception as e:
            print(f"⚠ Webhook registration failed: {e}")
            print("  Falling back to polling...")
    else:
        print("\n[Step 3] No webhook URL configured, will use polling")
    
    # Step 4: Create analysis task
    print("\n[Step 4] Creating analysis task...")
    prompt = """
    Please analyze this quarterly business report and provide:
    1. A summary of key findings
    2. Trends and insights
    3. Recommendations for next quarter
    
    Format the response as a structured report.
    """
    
    try:
        task = workflow.create_task(prompt, file_id=file_id)
        task_id = task.get("task_id")
        task_url = task.get("task_url")
        print(f"✓ Task created: {task_id}")
        print(f"  View at: {task_url}")
    except Exception as e:
        print(f"✗ Task creation failed: {e}")
        return
    
    # Step 5: Wait for completion
    if webhook_id:
        print("\n[Step 5] Waiting for webhook notification...")
        print("  The webhook will notify you when the task completes")
        print(f"  Check your webhook endpoint: {webhook_url}")
        print(f"  Or view task at: {task_url}")
        
        # In production, you'd return here and handle completion in webhook
        # For demo, we'll poll anyway
        input("\nPress Enter to check task status...")
    else:
        print("\n[Step 5] Polling for completion...")
    
    try:
        result = workflow.wait_for_completion(task_id)
        print(f"✓ Task completed!")
        print(f"  Status: {result.get('status')}")
        
        # Check for attachments
        attachments = result.get("attachments", [])
        if attachments:
            print(f"\n  Output files ({len(attachments)}):")
            for att in attachments:
                print(f"    - {att.get('filename')}")
                print(f"      Size: {att.get('size_bytes')} bytes")
                print(f"      URL: {att.get('url')}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Step 6: Cleanup
    if webhook_id:
        print("\n[Step 6] Cleaning up...")
        try:
            workflow.delete_webhook(webhook_id)
            print(f"✓ Webhook deleted")
        except Exception as e:
            print(f"⚠ Cleanup warning: {e}")
    
    print("\n" + "=" * 70)
    print("Workflow Complete!")
    print("=" * 70)
    print("\nIn a production system, you would:")
    print("  • Store task IDs in your database")
    print("  • Process webhook events asynchronously")
    print("  • Download and store result files")
    print("  • Send notifications to users")
    print("  • Trigger downstream workflows")
    print("=" * 70)


def run_multi_document_workflow():
    """
    Example: Process multiple documents in parallel.
    """
    print("=" * 70)
    print("Advanced Workflow: Batch Document Processing")
    print("=" * 70)
    
    workflow = ManusWorkflow()
    
    # Create sample documents
    documents = []
    for i in range(3):
        doc_path = f"document-{i+1}.txt"
        with open(doc_path, "w") as f:
            f.write(f"Document {i+1}\n\n")
            f.write(f"This is sample content for document {i+1}.\n")
        documents.append(doc_path)
    
    print(f"\n[Step 1] Created {len(documents)} sample documents")
    
    # Upload all documents
    print("\n[Step 2] Uploading documents...")
    file_ids = []
    for doc in documents:
        try:
            file_id = workflow.upload_file(doc)
            file_ids.append(file_id)
            print(f"  ✓ Uploaded: {doc} -> {file_id}")
        except Exception as e:
            print(f"  ✗ Failed: {doc} - {e}")
    
    # Create tasks for each document
    print("\n[Step 3] Creating analysis tasks...")
    task_ids = []
    for i, file_id in enumerate(file_ids):
        try:
            task = workflow.create_task(
                f"Summarize document {i+1}",
                file_id=file_id
            )
            task_ids.append(task["task_id"])
            print(f"  ✓ Task {i+1}: {task['task_id']}")
        except Exception as e:
            print(f"  ✗ Task {i+1} failed: {e}")
    
    print(f"\n[Step 4] Created {len(task_ids)} tasks")
    print("  In production, webhooks would notify you as each completes")
    print("  This enables parallel processing at scale")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "batch":
        run_multi_document_workflow()
    else:
        run_document_analysis_workflow()
