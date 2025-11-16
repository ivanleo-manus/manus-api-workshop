# Part 3: Webhooks

## Overview

In this section, you'll learn how to implement webhooks for event-driven AI workflows. Webhooks eliminate the need for polling and provide real-time notifications when tasks complete.

**Time**: 25 minutes

## Learning Objectives

- Understand the benefits of webhooks over polling
- Register webhook endpoints with Manus
- Handle webhook events in your application
- Build event-driven notification systems
- Implement production-ready webhook handlers

## Why Webhooks?

### Polling (Parts 1 & 2)

```python
while task.status == "running":
    time.sleep(5)  # Wait 5 seconds
    task = get_task_status(task_id)  # Make API call
```

**Problems**:
- Wastes API calls
- Adds latency (5-second delay minimum)
- Inefficient resource usage
- Doesn't scale well

### Webhooks (Event-Driven)

```python
# Your server receives a POST request when task completes
@app.route('/webhooks/manus', methods=['POST'])
def handle_webhook():
    data = request.json
    if data['event_type'] == 'task_stopped':
        process_completion(data)
```

**Benefits**:
- Real-time notifications
- No wasted API calls
- Efficient and scalable
- Production-ready pattern

## Webhook Events

Manus sends two types of webhook events:

### 1. task_created

Triggered immediately after task creation.

**Payload**:
```json
{
  "event_id": "task_created_task_abc123",
  "event_type": "task_created",
  "task_detail": {
    "task_id": "task_abc123",
    "task_title": "Generate quarterly report",
    "task_url": "https://manus.im/app/task_abc123"
  }
}
```

**Use Cases**:
- Track task creation in your database
- Send confirmation to user
- Update dashboard
- Start monitoring

### 2. task_stopped

Triggered when task completes or needs input.

**Payload**:
```json
{
  "event_id": "task_stopped_task_abc123",
  "event_type": "task_stopped",
  "task_detail": {
    "task_id": "task_abc123",
    "task_title": "Generate quarterly report",
    "task_url": "https://manus.im/app/task_abc123",
    "message": "I've completed the report...",
    "attachments": [
      {
        "file_name": "report.pdf",
        "url": "https://s3.amazonaws.com/...",
        "size_bytes": 2048576
      }
    ],
    "stop_reason": "finish"
  }
}
```

**Stop Reasons**:
- `"finish"` - Task completed successfully
- `"ask"` - Task needs user input to continue

## Exercise Instructions

### Step 1: Set Up Webhook Endpoint

You have three options:

#### Option A: webhook.site (Easiest)

1. Visit [webhook.site](https://webhook.site)
2. Copy your unique URL
3. Use it for testing (no code required)

#### Option B: Local Flask Server + ngrok

1. Run the webhook handler:
   ```bash
   python webhook-handler.py
   ```

2. In another terminal, expose it with ngrok:
   ```bash
   ngrok http 5000
   ```

3. Copy the ngrok URL (e.g., `https://abc123.ngrok.io`)

#### Option C: Deploy to Server

Deploy `webhook-handler.py` to any server with a public IP or domain.

### Step 2: Register Webhook

Run the solution script:

```bash
python solution.py
```

Enter your webhook URL when prompted.

### Step 3: Create Task and Observe Events

The script will create a task and you'll see webhook events arrive at your endpoint.

### Step 4: Implement Custom Handler

Modify `webhook-handler.py` to add your own logic:

```python
def handle_task_stopped(data):
    task_detail = data.get('task_detail', {})
    
    if task_detail.get('stop_reason') == 'finish':
        # Task completed - your custom logic here
        send_email_notification(task_detail)
        download_attachments(task_detail['attachments'])
        update_database(task_detail['task_id'], 'completed')
```

## Webhook Handler Implementation

### Basic Flask Handler

```python
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/webhooks/manus', methods=['POST'])
def handle_webhook():
    data = request.json
    event_type = data.get('event_type')
    
    if event_type == 'task_stopped':
        task_detail = data['task_detail']
        if task_detail['stop_reason'] == 'finish':
            # Process completion
            process_results(task_detail)
    
    return jsonify({'status': 'received'}), 200
```

### Security Considerations

In production, you should:

1. **Validate webhook source**:
   ```python
   # Check IP address or signature
   if request.remote_addr not in ALLOWED_IPS:
       return jsonify({'error': 'unauthorized'}), 403
   ```

2. **Use HTTPS**:
   - Always use HTTPS endpoints
   - Never expose HTTP webhooks publicly

3. **Implement idempotency**:
   ```python
   # Store processed event IDs
   event_id = data.get('event_id')
   if event_id in processed_events:
       return jsonify({'status': 'already_processed'}), 200
   ```

4. **Handle failures gracefully**:
   ```python
   try:
       process_webhook(data)
   except Exception as e:
       log_error(e)
       # Still return 200 to prevent retries
       return jsonify({'status': 'error'}), 200
   ```

## Real-World Integration Examples

### Example 1: Slack Notifications

```python
from slack_sdk import WebClient

slack_client = WebClient(token=SLACK_TOKEN)

def handle_task_stopped(data):
    task_detail = data['task_detail']
    
    if task_detail['stop_reason'] == 'finish':
        slack_client.chat_postMessage(
            channel='#ai-tasks',
            text=f"✓ Task completed: {task_detail['task_title']}\n"
                 f"View: {task_detail['task_url']}"
        )
```

### Example 2: Email Notifications

```python
import smtplib
from email.mime.text import MIMEText

def send_completion_email(task_detail):
    msg = MIMEText(f"Your task '{task_detail['task_title']}' is complete!")
    msg['Subject'] = 'Manus Task Completed'
    msg['From'] = 'noreply@yourapp.com'
    msg['To'] = 'user@example.com'
    
    with smtplib.SMTP('localhost') as server:
        server.send_message(msg)
```

### Example 3: Database Updates

```python
import psycopg2

def update_task_status(task_id, status, result_data):
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    cursor.execute(
        "UPDATE tasks SET status = %s, result = %s, completed_at = NOW() WHERE id = %s",
        (status, result_data, task_id)
    )
    
    conn.commit()
    conn.close()
```

## Testing Your Webhook

### Manual Testing with curl

```bash
curl -X POST http://localhost:5000/webhooks/manus \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "task_stopped",
    "event_id": "test_event_123",
    "task_detail": {
      "task_id": "test_task",
      "task_title": "Test Task",
      "stop_reason": "finish",
      "message": "Test complete"
    }
  }'
```

### Automated Testing

```python
import unittest
from webhook_handler import app

class TestWebhookHandler(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
    
    def test_task_stopped_event(self):
        payload = {
            "event_type": "task_stopped",
            "task_detail": {
                "stop_reason": "finish"
            }
        }
        
        response = self.client.post(
            '/webhooks/manus',
            json=payload
        )
        
        self.assertEqual(response.status_code, 200)
```

## Common Issues

### Issue: Webhook not receiving events

**Solutions**:
1. Verify webhook URL is publicly accessible
2. Check that webhook is registered (check API response)
3. Ensure endpoint returns 200 status code
4. Check firewall/security group settings

### Issue: Duplicate events

**Solution**: Implement idempotency using event IDs:

```python
processed_events = set()

def handle_webhook(data):
    event_id = data['event_id']
    if event_id in processed_events:
        return  # Already processed
    
    process_event(data)
    processed_events.add(event_id)
```

### Issue: Webhook endpoint timeout

**Solution**: Process webhooks asynchronously:

```python
from threading import Thread

@app.route('/webhooks/manus', methods=['POST'])
def handle_webhook():
    data = request.json
    
    # Process in background thread
    Thread(target=process_webhook, args=(data,)).start()
    
    # Return immediately
    return jsonify({'status': 'received'}), 200
```

## Production Best Practices

1. **Respond quickly**: Return 200 within 10 seconds
2. **Process asynchronously**: Use background jobs for heavy processing
3. **Log everything**: Keep audit trail of webhook events
4. **Monitor failures**: Alert on webhook processing errors
5. **Implement retries**: Handle transient failures gracefully
6. **Secure your endpoint**: Use HTTPS and validate requests
7. **Scale horizontally**: Use load balancers for high volume

## Next Steps

Now that you understand webhooks, move on to [Part 4: Complete Workflow](../04-complete-workflow/) to see everything working together in a production-ready example.

## Additional Resources

- [Webhook Documentation](https://open.manus.ai/docs/webhooks)
- [Webhook Security Best Practices](https://open.manus.ai/docs/webhooks#security)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [ngrok Documentation](https://ngrok.com/docs)
