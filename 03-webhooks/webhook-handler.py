"""
Part 3: Webhook Handler - Flask Application

This is a simple Flask application that receives webhook events from Manus.
It demonstrates how to handle task_created and task_stopped events.

Run this in a separate terminal:
    python webhook-handler.py

Then use ngrok or webhook.site to expose it publicly.
"""

from flask import Flask, request, jsonify
from datetime import datetime
import json

app = Flask(__name__)

# Store received events for demonstration
received_events = []


@app.route('/webhooks/manus', methods=['POST'])
def handle_webhook():
    """
    Handle incoming webhook events from Manus.
    
    Manus sends two types of events:
    1. task_created - When a task is created
    2. task_stopped - When a task completes or needs input
    """
    try:
        # Parse the webhook payload
        data = request.json
        event_type = data.get('event_type')
        event_id = data.get('event_id')
        
        # Log the event
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"\n[{timestamp}] Received webhook event")
        print(f"Event Type: {event_type}")
        print(f"Event ID: {event_id}")
        
        # Handle different event types
        if event_type == 'task_created':
            handle_task_created(data)
        elif event_type == 'task_stopped':
            handle_task_stopped(data)
        else:
            print(f"Unknown event type: {event_type}")
        
        # Store event for later inspection
        received_events.append({
            'timestamp': timestamp,
            'event_type': event_type,
            'data': data
        })
        
        # Return 200 OK to acknowledge receipt
        return jsonify({'status': 'received'}), 200
        
    except Exception as e:
        print(f"Error handling webhook: {e}")
        return jsonify({'error': str(e)}), 500


def handle_task_created(data):
    """
    Handle task_created event.
    
    Payload structure:
    {
        "event_id": "task_created_task_abc123",
        "event_type": "task_created",
        "task_detail": {
            "task_id": "task_abc123",
            "task_title": "...",
            "task_url": "https://manus.im/app/task_abc123"
        }
    }
    """
    task_detail = data.get('task_detail', {})
    task_id = task_detail.get('task_id')
    task_title = task_detail.get('task_title')
    task_url = task_detail.get('task_url')
    
    print(f"  Task Created:")
    print(f"    ID: {task_id}")
    print(f"    Title: {task_title}")
    print(f"    URL: {task_url}")
    
    # Here you could:
    # - Store task info in database
    # - Send notification to user
    # - Update dashboard
    # - Trigger other workflows


def handle_task_stopped(data):
    """
    Handle task_stopped event.
    
    Payload structure:
    {
        "event_id": "task_stopped_task_abc123",
        "event_type": "task_stopped",
        "task_detail": {
            "task_id": "task_abc123",
            "task_title": "...",
            "task_url": "https://manus.im/app/task_abc123",
            "message": "...",
            "attachments": [...],
            "stop_reason": "finish" | "ask"
        }
    }
    """
    task_detail = data.get('task_detail', {})
    task_id = task_detail.get('task_id')
    task_title = task_detail.get('task_title')
    stop_reason = task_detail.get('stop_reason')
    message = task_detail.get('message')
    attachments = task_detail.get('attachments', [])
    
    print(f"  Task Stopped:")
    print(f"    ID: {task_id}")
    print(f"    Title: {task_title}")
    print(f"    Stop Reason: {stop_reason}")
    
    if stop_reason == 'finish':
        print(f"    ✓ Task completed successfully!")
        print(f"    Message: {message[:100]}..." if len(message) > 100 else f"    Message: {message}")
        
        if attachments:
            print(f"    Attachments: {len(attachments)}")
            for att in attachments:
                print(f"      - {att.get('file_name')} ({att.get('size_bytes')} bytes)")
        
        # Here you could:
        # - Download result files
        # - Send completion notification
        # - Update database status
        # - Trigger next workflow step
        
    elif stop_reason == 'ask':
        print(f"    ⏸ Task needs user input")
        print(f"    Question: {message}")
        
        # Here you could:
        # - Notify user to provide input
        # - Show prompt in UI
        # - Queue for human review


@app.route('/events', methods=['GET'])
def list_events():
    """
    List all received events (for debugging).
    """
    return jsonify({
        'total_events': len(received_events),
        'events': received_events
    })


@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint.
    """
    return jsonify({'status': 'healthy', 'service': 'manus-webhook-handler'})


if __name__ == '__main__':
    print("=" * 60)
    print("Manus Webhook Handler")
    print("=" * 60)
    print("\nStarting Flask server on http://localhost:5000")
    print("\nEndpoints:")
    print("  POST /webhooks/manus - Webhook receiver")
    print("  GET  /events         - List received events")
    print("  GET  /health         - Health check")
    print("\nTo expose this locally for testing:")
    print("  1. Use webhook.site for quick testing")
    print("  2. Use ngrok: ngrok http 5000")
    print("  3. Use localtunnel: lt --port 5000")
    print("\n" + "=" * 60 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
