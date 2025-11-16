# Part 2: File Handling

## Overview

In this section, you'll learn how to work with files in the Manus API. This is essential for document processing, data analysis, and any task that requires the AI agent to work with your content.

**Time**: 30 minutes

## Learning Objectives

- Upload files to Manus using the two-step process
- Attach files to tasks
- Create tasks with multiple attachment types
- Retrieve and handle task output attachments

## File Upload Process

Manus uses a two-step file upload process for security and efficiency:

### Step 1: Create File Record

Request a presigned upload URL:

```python
POST /v1/files
{
    "filename": "document.pdf"
}
```

Response:
```python
{
    "id": "file-abc123",
    "filename": "document.pdf",
    "status": "pending",
    "upload_url": "https://s3.amazonaws.com/...",
    "upload_expires_at": "2024-01-01T12:03:00Z",
    "created_at": "2024-01-01T12:00:00Z"
}
```

### Step 2: Upload File Content

Upload the actual file to the presigned URL:

```python
PUT <upload_url>
Content: <file bytes>
```

**Important**: The upload URL expires in **3 minutes**. Complete the upload quickly.

## Attachment Types

Manus supports three types of attachments:

### 1. File ID Attachment

Use a previously uploaded file:

```python
{
    "attachments": [
        {
            "file_id": "file-abc123"
        }
    ]
}
```

### 2. URL Attachment

Reference a publicly accessible URL:

```python
{
    "attachments": [
        {
            "url": "https://example.com/document.pdf",
            "filename": "document.pdf"
        }
    ]
}
```

### 3. Base64 Data Attachment

Embed file content directly (for small files):

```python
{
    "attachments": [
        {
            "data": "base64-encoded-content",
            "filename": "document.txt",
            "mime_type": "text/plain"
        }
    ]
}
```

## Exercise Instructions

### Step 1: Implement upload_file()

This function handles the two-step upload process:

1. Create file record with POST to `/files`
2. Upload content with PUT to the presigned URL
3. Return the file ID

**Key Points**:
- Extract filename from the file path
- Read file in binary mode (`"rb"`)
- The presigned URL expires in 3 minutes
- Uploaded files auto-delete after 48 hours

### Step 2: Implement create_task_with_file()

Create a task with a file attachment:

```python
{
    "prompt": "Analyze this document",
    "agentProfile": "manus-1.5",
    "attachments": [
        {
            "file_id": "file-abc123"
        }
    ]
}
```

### Step 3: Implement get_task_result()

Retrieve the complete task details, including any output attachments the agent created.

### Step 4: Run Your Code

```bash
python starter.py
```

## Expected Output

```
============================================================
Part 2: File Handling
============================================================

[Step 1] Uploading file...
  Created file record: file-abc123xyz
  Uploaded file content (234 bytes)
✓ File uploaded successfully!
  File ID: file-abc123xyz

[Step 2] Creating task with file attachment...
✓ Task created with file attachment!
  Task ID: task-xyz789

[Step 3] Waiting for task to complete...
  Status: running
  Status: running
  Status: completed
✓ Task completed!
  Status: completed
  Output attachments: 1
    - analysis-summary.md

============================================================
Part 2 Complete! You've successfully:
  • Uploaded a file to Manus
  • Created a task with file attachment
  • Retrieved task results
============================================================
```

## Key Concepts

### File Lifecycle

1. **Upload**: File is uploaded and gets a unique ID
2. **Attach**: File ID is included in task creation
3. **Process**: Agent accesses and analyzes the file
4. **Expire**: File auto-deletes after 48 hours

### Multiple Attachments

You can attach multiple files to a single task:

```python
{
    "attachments": [
        {"file_id": "file-1"},
        {"file_id": "file-2"},
        {"url": "https://example.com/file3.pdf", "filename": "file3.pdf"}
    ]
}
```

### Output Attachments

When tasks complete, the agent may create output files (reports, visualizations, etc.). These are included in the task result:

```python
{
    "status": "completed",
    "attachments": [
        {
            "filename": "analysis-report.pdf",
            "url": "https://s3.amazonaws.com/...",
            "size_bytes": 102400
        }
    ]
}
```

## Common Issues

### Issue: "Upload URL expired"

**Solution**: The presigned URL expires in 3 minutes. If you see this error, create a new file record and try again.

### Issue: "File not found"

**Solution**: Files auto-delete after 48 hours. Upload files shortly before creating tasks that use them.

### Issue: "Invalid file format"

**Solution**: Manus supports most common formats (PDF, DOCX, TXT, CSV, images, etc.). Check the documentation for the full list.

## Best Practices

### For Production Systems

1. **Upload files just before task creation** to avoid the 48-hour expiration
2. **Handle upload failures gracefully** with retry logic
3. **Validate file sizes** before uploading (check API limits)
4. **Use appropriate attachment types**:
   - File ID: For files you upload
   - URL: For publicly accessible files
   - Base64: Only for very small files (<1MB)

### For Large Files

1. **Check file size limits** in the API documentation
2. **Consider compressing** large documents
3. **Use streaming uploads** for very large files
4. **Monitor upload progress** for better UX

## Next Steps

Now that you can work with files, move on to [Part 3: Webhooks](../03-webhooks/) to learn how to receive real-time notifications when tasks complete.

## Additional Resources

- [File Upload API Reference](https://open.manus.ai/docs/api-reference/create-file)
- [Create Task with Attachments](https://open.manus.ai/docs/api-reference/create-task)
- [Supported File Formats](https://open.manus.ai/docs)
