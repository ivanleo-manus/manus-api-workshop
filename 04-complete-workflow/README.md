# Part 4: Complete Workflow

## Overview

This section brings everything together into a production-ready workflow. You'll see how to combine file uploads, task creation, and webhook notifications into a cohesive system.

**Time**: 10 minutes

## Learning Objectives

- Understand production-ready workflow patterns
- Implement error handling and retry logic
- Manage configuration properly
- Build scalable batch processing systems
- Apply best practices from Parts 1-3

## Architecture

### Single Document Workflow

```
┌─────────────┐
│   Upload    │
│  Document   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Register   │
│   Webhook   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Create    │
│    Task     │
└──────┬──────┘
       │
       ▼
┌─────────────┐     ┌──────────────┐
│   Webhook   │────▶│   Process    │
│    Event    │     │   Results    │
└─────────────┘     └──────────────┘
```

### Batch Processing Workflow

```
┌──────────┐  ┌──────────┐  ┌──────────┐
│  Doc 1   │  │  Doc 2   │  │  Doc 3   │
└────┬─────┘  └────┬─────┘  └────┬─────┘
     │             │             │
     └─────────────┼─────────────┘
                   │
                   ▼
          ┌────────────────┐
          │  Upload All    │
          └────────┬───────┘
                   │
                   ▼
          ┌────────────────┐
          │  Create Tasks  │
          │   (Parallel)   │
          └────────┬───────┘
                   │
                   ▼
          ┌────────────────┐
          │    Webhooks    │
          │  (As Complete) │
          └────────────────┘
```

## Running the Examples

### Single Document Analysis

```bash
python workflow.py
```

This demonstrates:
- Document upload
- Webhook registration
- Task creation
- Completion handling
- Cleanup

### Batch Processing

```bash
python workflow.py batch
```

This demonstrates:
- Multiple file uploads
- Parallel task creation
- Scalable processing patterns

## Code Structure

### ManusWorkflow Class

The `ManusWorkflow` class encapsulates all API interactions:

```python
workflow = ManusWorkflow()

# Upload file
file_id = workflow.upload_file("document.pdf")

# Create task
task = workflow.create_task("Analyze this", file_id=file_id)

# Register webhook
webhook = workflow.register_webhook("https://your-app.com/webhook")

# Wait for completion (fallback)
result = workflow.wait_for_completion(task["task_id"])
```

### Benefits of This Approach

1. **Encapsulation**: All API logic in one place
2. **Reusability**: Easy to use across your application
3. **Testability**: Simple to mock for unit tests
4. **Maintainability**: Changes to API are isolated

## Production Best Practices

### 1. Error Handling

```python
def create_task_with_retry(self, prompt, max_retries=3):
    """
    Create task with automatic retry on failure.
    """
    for attempt in range(max_retries):
        try:
            return self.create_task(prompt)
        except requests.exceptions.RequestException as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)  # Exponential backoff
```

### 2. Configuration Management

Use environment variables and config files:

```python
# .env file
MANUS_API_KEY=your-key
WEBHOOK_URL=https://your-app.com/webhook
LOG_LEVEL=INFO

# config.py
class Config:
    MANUS_API_KEY = os.getenv("MANUS_API_KEY")
    WEBHOOK_URL = os.getenv("WEBHOOK_URL")
```

### 3. Logging

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_task(self, prompt):
    logger.info(f"Creating task: {prompt[:50]}...")
    try:
        task = self._make_request(...)
        logger.info(f"Task created: {task['task_id']}")
        return task
    except Exception as e:
        logger.error(f"Task creation failed: {e}")
        raise
```

### 4. Monitoring

Track key metrics:

```python
from prometheus_client import Counter, Histogram

task_counter = Counter('manus_tasks_created', 'Total tasks created')
task_duration = Histogram('manus_task_duration', 'Task completion time')

def create_task(self, prompt):
    task_counter.inc()
    start_time = time.time()
    
    task = self._make_request(...)
    
    duration = time.time() - start_time
    task_duration.observe(duration)
    
    return task
```

### 5. Database Integration

Store task metadata:

```python
def create_task_with_db(self, prompt, user_id):
    # Create task via API
    task = self.create_task(prompt)
    
    # Store in database
    db.execute(
        "INSERT INTO tasks (id, user_id, status, created_at) VALUES (?, ?, ?, ?)",
        (task['task_id'], user_id, 'running', datetime.now())
    )
    
    return task

def handle_webhook(data):
    task_id = data['task_detail']['task_id']
    status = data['task_detail']['stop_reason']
    
    # Update database
    db.execute(
        "UPDATE tasks SET status = ?, completed_at = ? WHERE id = ?",
        (status, datetime.now(), task_id)
    )
```

## Use Case Examples

### 1. Document Processing Pipeline

```python
def process_document_pipeline(document_path, user_id):
    """
    Complete document processing workflow.
    """
    workflow = ManusWorkflow()
    
    # Upload document
    file_id = workflow.upload_file(document_path)
    
    # Create analysis task
    task = workflow.create_task(
        "Extract key information and create summary",
        file_id=file_id
    )
    
    # Store in database
    store_task(task['task_id'], user_id, 'processing')
    
    # Webhook will handle completion
    return task['task_id']
```

### 2. Automated Research Assistant

```python
def research_query(query, sources):
    """
    Research a topic across multiple sources.
    """
    workflow = ManusWorkflow()
    
    # Upload source documents
    file_ids = [workflow.upload_file(src) for src in sources]
    
    # Create research task
    prompt = f"""
    Research the following query using the provided sources:
    {query}
    
    Provide:
    1. Summary of findings
    2. Key insights
    3. Citations from sources
    """
    
    task = workflow.create_task(prompt, file_id=file_ids[0])
    
    return task
```

### 3. Batch Email Processing

```python
def process_email_batch(email_ids):
    """
    Process multiple emails in parallel.
    """
    workflow = ManusWorkflow()
    task_ids = []
    
    for email_id in email_ids:
        email_content = fetch_email(email_id)
        
        task = workflow.create_task(
            f"Categorize and suggest response for email {email_id}",
            file_id=None  # Could attach email as file
        )
        
        task_ids.append(task['task_id'])
    
    # Webhooks will notify as each completes
    return task_ids
```

## Scaling Considerations

### Handling High Volume

1. **Use webhooks instead of polling**
   - Eliminates constant API calls
   - Reduces latency
   - Scales better

2. **Implement rate limiting**
   ```python
   from ratelimit import limits, sleep_and_retry
   
   @sleep_and_retry
   @limits(calls=100, period=60)  # 100 calls per minute
   def create_task(self, prompt):
       return self._make_request(...)
   ```

3. **Use connection pooling**
   ```python
   from requests.adapters import HTTPAdapter
   
   session = requests.Session()
   adapter = HTTPAdapter(pool_connections=100, pool_maxsize=100)
   session.mount('https://', adapter)
   ```

4. **Implement caching**
   ```python
   from functools import lru_cache
   
   @lru_cache(maxsize=1000)
   def get_task(self, task_id):
       return self._make_request(f"/tasks/{task_id}")
   ```

### Async Processing

For high-throughput systems, use async/await:

```python
import asyncio
import aiohttp

class AsyncManusWorkflow:
    async def create_task(self, prompt):
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/tasks",
                headers=self.headers,
                json={"prompt": prompt}
            ) as response:
                return await response.json()
    
    async def create_tasks_batch(self, prompts):
        tasks = [self.create_task(p) for p in prompts]
        return await asyncio.gather(*tasks)
```

## Testing

### Unit Tests

```python
import unittest
from unittest.mock import Mock, patch

class TestManusWorkflow(unittest.TestCase):
    def setUp(self):
        self.workflow = ManusWorkflow(api_key="test-key")
    
    @patch('requests.Session.post')
    def test_create_task(self, mock_post):
        mock_post.return_value.json.return_value = {
            "task_id": "test-123"
        }
        
        task = self.workflow.create_task("Test prompt")
        
        self.assertEqual(task["task_id"], "test-123")
        mock_post.assert_called_once()
```

### Integration Tests

```python
def test_complete_workflow():
    """
    Test the entire workflow end-to-end.
    """
    workflow = ManusWorkflow()
    
    # Create test document
    with open("test.txt", "w") as f:
        f.write("Test content")
    
    # Run workflow
    file_id = workflow.upload_file("test.txt")
    task = workflow.create_task("Analyze", file_id=file_id)
    
    assert task["task_id"] is not None
    
    # Cleanup
    os.remove("test.txt")
```

## Next Steps

Congratulations! You've completed the workshop. You now have:

- ✓ Understanding of Manus API fundamentals
- ✓ File upload and management skills
- ✓ Webhook implementation knowledge
- ✓ Production-ready workflow patterns

### Continue Learning

1. **Explore connectors**: Integrate Gmail, Notion, Calendar
2. **Try OpenAI SDK compatibility**: Migrate existing OpenAI code
3. **Build your own application**: Apply these patterns to your use case
4. **Join the community**: Share your projects and learn from others

## Additional Resources

- [Manus API Documentation](https://open.manus.ai/docs)
- [Production Deployment Guide](../docs/setup-guide.md)
- [Troubleshooting Guide](../docs/troubleshooting.md)
- [Community Forum](https://help.manus.im)
