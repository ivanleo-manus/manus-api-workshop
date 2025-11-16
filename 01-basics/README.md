# Part 1: Manus API Basics

## Overview

In this section, you'll learn the fundamentals of working with the Manus API. By the end, you'll be able to create tasks, check their status, and retrieve results.

**Time**: 20 minutes

## Learning Objectives

- Understand Manus API authentication
- Create your first AI task
- Check task status programmatically
- Implement basic polling for task completion
- Understand task lifecycle states

## Task Lifecycle States

Tasks in Manus go through several states:

| State | Description |
|-------|-------------|
| `running` | The agent is actively working on your request |
| `pending` | The agent needs user input to continue |
| `completed` | The task finished successfully |
| `error` | The task encountered an error |

## Exercise Instructions

### Step 1: Review the Starter Code

Open `starter.py` and review the structure. You'll see three main functions to implement:

1. `create_task()` - Creates a new task
2. `get_task_status()` - Retrieves task status
3. `wait_for_completion()` - Polls until task completes

### Step 2: Implement create_task()

This function sends a POST request to create a new task.

**API Endpoint**: `POST /v1/tasks`

**Required Headers**:
```python
{
    "API_KEY": "your-api-key",
    "Content-Type": "application/json"
}
```

**Request Body**:
```python
{
    "prompt": "Your task instruction",
    "agentProfile": "manus-1.5"  # or "manus-1.5-lite"
}
```

**Response**:
```python
{
    "task_id": "abc123...",
    "task_title": "Generated title",
    "task_url": "https://manus.im/app/abc123...",
    "share_url": "..."  # if createShareableLink was true
}
```

### Step 3: Implement get_task_status()

This function retrieves the current status of a task.

**API Endpoint**: `GET /v1/tasks/{task_id}`

**Required Headers**:
```python
{
    "API_KEY": "your-api-key"
}
```

**Response**:
```python
{
    "task_id": "abc123...",
    "status": "running",  # or "pending", "completed", "error"
    "task_url": "...",
    # ... other fields
}
```

### Step 4: Implement wait_for_completion()

This function polls the task status until it's no longer running.

**Algorithm**:
1. Start a timer
2. Loop while under max_wait time:
   - Get task status
   - If status is not "running", return the task
   - Print status update
   - Sleep for check_interval seconds
3. If timeout reached, raise TimeoutError

### Step 5: Run Your Code

```bash
python starter.py
```

If you get stuck, check `solution.py` for the complete implementation.

## Expected Output

When you run the solution successfully, you should see:

```
============================================================
Part 1: Manus API Basics
============================================================

[Step 1] Creating a task...
✓ Task created successfully!
  Task ID: abc123xyz...
  Task URL: https://manus.im/app/abc123xyz...

[Step 2] Checking task status...
✓ Current status: running

[Step 3] Waiting for task to complete...
  Status: running (checked at 14:23:45)
  Status: running (checked at 14:23:50)
  Status: completed (checked at 14:23:55)
✓ Task completed!
  Final status: completed

============================================================
Part 1 Complete! You've successfully:
  • Created a task via the API
  • Checked task status
  • Waited for task completion
============================================================
```

## Key Concepts

### Authentication

The Manus API uses API key authentication via a custom header:

```python
headers = {
    "API_KEY": "your-api-key-here"
}
```

### Agent Profiles

Manus offers different agent profiles:

- **manus-1.5**: Full-featured agent (default, previously "quality")
- **manus-1.5-lite**: Faster, lighter agent (previously "speed")

### Polling Strategy

Polling is the simplest way to check task status:

**Pros**:
- Easy to implement
- No infrastructure required
- Good for development/testing

**Cons**:
- Inefficient (wastes API calls)
- Adds latency
- Not ideal for production

In Part 3, we'll learn about webhooks, which solve these problems.

## Common Issues

### Issue: "MANUS_API_KEY not found"

**Solution**: Create a `.env` file in the project root:

```bash
MANUS_API_KEY=your-actual-api-key
```

### Issue: "401 Unauthorized"

**Solution**: Check that your API key is correct and active.

### Issue: Task stays in "running" state

**Solution**: Some tasks take longer. Increase `max_wait` parameter or check the task URL in your browser.

## Next Steps

Once you've completed this section, move on to [Part 2: File Handling](../02-file-handling/) to learn how to work with documents and attachments.

## Additional Resources

- [Manus API Documentation](https://open.manus.ai/docs)
- [Create Task API Reference](https://open.manus.ai/docs/api-reference/create-task)
- [Get Task API Reference](https://open.manus.ai/docs/api-reference/get-task)
