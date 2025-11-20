import modal
import os
import requests
import json
import fastapi
import re
from slack_sdk.signature import SignatureVerifier
from slack_sdk.web.client import WebClient
from slack_sdk.web.slack_response import SlackResponse
from dataclasses import dataclass
from typing import TypedDict, Optional


# --- Modal App Setup ---
app = modal.App("slack-manus-bridge")
image = modal.Image.debian_slim().pip_install(
    "fastapi[standard]", "requests", "slack-sdk"
)

FileID = str


@dataclass
class SlackFileAttachment:
    """A simple data class to represent a file to be attached to a Slack message."""

    filename: str
    url: str

class FileIDAttachment(TypedDict):
    """Defines the structure for a File ID attachment for the Manus API."""
    file_id: str
    filename: str


slack_secret = modal.Secret.from_name("slack-credentials")
manus_secret = modal.Secret.from_name("manus-api-key")

thread_task_map = modal.Dict.from_name("thread-task-map", create_if_missing=True)
task_info_map = modal.Dict.from_name(
    "slack-task-to-info-map", create_if_missing=True
)

class AppMentionEvent(TypedDict):
    type: str
    channel: str
    ts: str
    text: str
    user: str
    files: list[dict]

def upload_file_to_manus(file_content: bytes, filename: str) -> str:
    """
    Uploads a file to the Manus workspace and returns its file_id.
    """
    api_key = os.environ["MANUS_API_KEY"]
    base_url = "https://api.manus.ai/v1"

    # Step 1: Create a file record and get a presigned upload URL
    headers = {"API_KEY": api_key, "Content-Type": "application/json"}
    create_file_response = requests.post(
        f"{base_url}/files",
        headers=headers,
        json={"filename": filename}
    )
    create_file_response.raise_for_status()
    file_record = create_file_response.json()
    
    file_id = file_record["id"]
    upload_url = file_record["upload_url"]
    print(f"✓ File record created for '{filename}'. File ID: {file_id}")

    # Step 2: Upload the file content to the presigned URL
    upload_response = requests.put(
        upload_url,
        data=file_content,
        headers={"Content-Type": "application/octet-stream"} # Use octet-stream for raw bytes
    )
    upload_response.raise_for_status()
    
    print(f"✓ File '{filename}' uploaded successfully!")
    return file_id

def convert_to_slack_mrkdwn(text: str) -> str:
    """
    Converts standard Markdown to Slack mrkdwn.
    """
    if not text:
        return text
        
    # Bold: **text** -> *text*
    text = re.sub(r'\*\*(.*?)\*\*', r'*\1*', text)
    
    # Links: [text](url) -> <url|text>
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<\2|\1>', text)
    
    return text


def markdown_to_slack_blocks(text: str) -> list[dict]:
    """
    Parses markdown text and converts it into a list of Slack Block Kit blocks.
    Handles headers (###) and dividers (---).
    """
    blocks = []
    lines = text.split('\n')
    current_section_lines = []

    def flush_section():
        if current_section_lines:
            # Join lines and convert standard markdown to slack mrkdwn
            section_text = "\n".join(current_section_lines).strip()
            if section_text:
                # Convert standard markdown to slack mrkdwn
                section_text = convert_to_slack_mrkdwn(section_text)
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": section_text
                    }
                })
            current_section_lines.clear()

    for line in lines:
        # Check for headers (e.g. ### Header) - Slack headers are plain text only
        header_match = re.match(r'^(#{1,6})\s+(.+)$', line)
        # Check for dividers (e.g. ---)
        divider_match = re.match(r'^[-*_]{3,}$', line.strip())

        if header_match:
            flush_section()
            header_text = header_match.group(2)
            blocks.append({
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": header_text[:3000], # Max length for header
                    "emoji": True
                }
            })
        elif divider_match:
            flush_section()
            blocks.append({"type": "divider"})
        else:
            current_section_lines.append(line)
            
    flush_section()
    return blocks


def get_slack_client() -> WebClient:
    return WebClient(token=os.environ.get("SLACK_BOT_TOKEN"))


def upload_files(channel: str, files: list[SlackFileAttachment], thread_ts: str) -> list[FileID]:
    client = get_slack_client()
    file_ids = []
    for file in files:
        response: SlackResponse = client.files_upload_v2(
            channel=channel,
            filename=file.filename,
            content=requests.get(file.url).content,
            thread_ts=thread_ts,
        )
        if not response.get("ok"):
            print(f"Error uploading {file.filename}: {response.get('error')}")
        else:
            file_ids.append(response.get("file").get("id"))
    return file_ids




def post_slack_message(
    channel: str,
    thread_ts: str,
    text: str, # Fallback text for notifications
    blocks: Optional[list[dict[str, any]]] = None,
    files: Optional[list[SlackFileAttachment]] = None,
) -> SlackResponse:
    """
    Posts a message with rich blocks and optional file attachments to a 
    specific Slack channel and thread.
    """
    client = get_slack_client()
    attachments: list[FileID] = []
    if files:
        attachments = upload_files(channel, files, thread_ts)

    response: SlackResponse = client.chat_postMessage(
        channel=channel,
        thread_ts=thread_ts,
        text=text,
        blocks=blocks, # Add blocks for rich formatting
        files=attachments,
    )

    if not response.get("ok"):
        print(f"Error posting to Slack: {response.get('error')}")
    return response


def create_manus_task(prompt: str, task_id: Optional[str] = None, attachments: Optional[list[FileIDAttachment]] = None) -> dict:
    api_key = os.environ["MANUS_API_KEY"]
    base_url = "https://api.manus.ai/v1"
    payload = {
        "prompt": f"""
You're a helpful assistant for company policy questions. 

1. Use the Notion connector to retrieve the most up-to-date version of the company policy before answering.
2. Figure out the answer to the user's question based on the current policy. Provide inline citations from the policy whenever relevant.
3. If the user's question relates to a travel expense:
   - Create a new page or update an existing page for the user about their trip.
   - Use the date of the travel expense to determine which trip or item should be updated or referenced.

Respond helpfully and accurately, following the steps above.

<user_request>
{prompt}
</user_request>
        """,
        "agentProfile": "manus-1.5",
        "taskMode": "agent",
        "connectors":["9c27c684-2f4f-4d33-8fcf-51664ea15c00"]
    }
    if task_id:
        payload["taskId"] = task_id
    
    if attachments:
        payload["attachments"] = attachments

    response = requests.post(
        f"{base_url}/tasks",
        headers={"API_KEY": api_key},
        json=payload,
    )
    return response.json()

def handle_manus_response(payload: dict) -> None:
    """
    Handles the 'task_stopped' event from Manus, fetching the full task output
    and posting all new assistant messages back to the originating Slack thread.
    """
    if payload.get("event_type") != "task_stopped":
        return

    task_id = payload.get("task_detail", {}).get("task_id")
    if not task_id:
        return

    # 1. Look up the corresponding Slack thread information
    slack_info = task_info_map.get(task_id)
    if not slack_info:
        print(f"Warning: Received Manus event for untracked task_id: {task_id}")
        return

    # 2. Fetch the full task details from the Manus API
    api_key = os.environ["MANUS_API_KEY"]
    base_url = "https://api.manus.ai/v1"
    response = requests.get(f"{base_url}/tasks/{task_id}", headers={"API_KEY": api_key})
    full_task = response.json()

    # 3. Find the last user message and post all subsequent assistant messages
    output_history = full_task.get("output", [])
    # Iterate backwards to find the last message from the user
    for i in range(len(output_history) - 1, -1, -1):
        if output_history[i].get("role") == "user":
            last_user_index = i
            break

    # Get all messages that came after the last user message
    messages_to_post = output_history[last_user_index + 1 :]

    # 4. Post each of these messages back to the Slack thread
    for message in messages_to_post:
        if message.get("role") != "assistant":
            continue

        # Extract text and files from the content
        text_content = ""
        message_blocks = []
        attachments = []
        
        for content in message.get("content", []):
            if content.get("type") == "output_text":
                raw_text = content.get("text")
                text_content = convert_to_slack_mrkdwn(raw_text)
                # Convert the raw markdown into rich blocks
                message_blocks = markdown_to_slack_blocks(raw_text)
            elif content.get("type") == "output_file":
                attachments.append(
                    SlackFileAttachment(
                        filename=content.get("fileName"), url=content.get("fileUrl")
                    )
                )
        
        # Post the message to Slack if it has content
        if text_content or attachments:
            post_slack_message(
                channel=slack_info["channel_id"],
                thread_ts=slack_info["thread_id"],
                text=text_content, # Fallback text for notifications
                blocks=message_blocks, # Rich blocks
                files=attachments,
            )

def handle_slack_message(event: AppMentionEvent) -> None:
    """
    Handles Slack mentions, creating a new Manus task for the first message in a
    thread and continuing the task for any follow-up messages.
    """
    channel_id = event["channel"]
    # Use thread_ts if it exists, otherwise fall back to the message's own ts.
    # This correctly identifies the conversation thread.
    thread_id = event.get("thread_ts", event["ts"])
    
    # Clean the prompt text
    raw_text = event.get("text", "")
    prompt_text = re.sub(r"^<@[\w\d]+>\s*", "", raw_text)

    client = get_slack_client()
    
    # Check if a task already exists for this thread
    existing_task_id = thread_task_map.get(thread_id)

    manus_attachments: list[FileIDAttachment] = []
    if "files" in event:
        print(f"Found {len(event['files'])} files in the Slack message.")
        for file in event["files"]:
            file_url = file["url_private_download"]
            file_name = file["name"]
            
            # Download the file using the authenticated Slack URL
            response = requests.get(
                file_url,
                headers={"Authorization": f"Bearer {os.environ['SLACK_BOT_TOKEN']}"}
            )
            response.raise_for_status()
            
            # Upload the file to Manus and get the file_id
            file_id = upload_file_to_manus(response.content, file_name)
            
            # Prepare the attachment for the Manus task
            manus_attachments.append({
                "file_id": file_id,
                "filename": file_name,
            })
    
    if existing_task_id:
        # --- This is a follow-up message ---
        print(f"Continuing existing task {existing_task_id} for thread {thread_id}")
        create_manus_task(prompt_text, task_id=existing_task_id, attachments=manus_attachments)
        
        # Add a reaction to acknowledge the message without cluttering the thread
        client.reactions_add(
            channel=channel_id, 
            name="eyes",  # A simple "I'm looking at this" emoji
            timestamp=event["ts"]
        )
        return
        
    manus_task = create_manus_task(prompt_text, attachments=manus_attachments)
    new_task_id = manus_task.get("task_id")
    task_url = manus_task.get("task_url")

    # Save the mapping to our dictionary for future lookups
    thread_task_map[thread_id] = new_task_id
    task_info_map[new_task_id] = {
        "thread_id": thread_id,
        "channel_id": channel_id,
    }
    # Post the rich "Task Created" message with the button
    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "We've started working on your request!"
            }
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "View on Web 🌐",
                        "emoji": True
                    },
                    "url": task_url
                }
            ]
        }
    ]

    client.chat_postMessage(
        channel=channel_id,
        thread_ts=thread_id,
        blocks=blocks,
        text=f"Task created! View progress: {task_url}"
    )


@app.function(image=image, secrets=[slack_secret, manus_secret])
@modal.asgi_app()
def fastapi_app():
    web_app = fastapi.FastAPI()

    @web_app.get("/")
    async def wakeup():
        return {"status": "ok"}

    
    @web_app.post("/webhooks/manus")
    async def manus_events(
        request: fastapi.Request, background_tasks: fastapi.BackgroundTasks
    ):
        """Handles all incoming webhook events from Manus."""
        payload = await request.json()
        print("Received Manus Event:")
        print(json.dumps(payload, indent=2))
        
        background_tasks.add_task(handle_manus_response, payload)
        return {"status": "ok"}

    @web_app.post("/webhooks/slack")
    async def slack_events(
        request: fastapi.Request, background_tasks: fastapi.BackgroundTasks
    ):
        """
        Handles all incoming webhook events from Slack.
        """
        # 1. Get the raw request body for signature verification
        body = await request.body()
        headers = request.headers

        # 2. Verify the request is authentically from Slack (critical security step!)
        verifier = SignatureVerifier(os.environ["SLACK_SIGNING_SECRET"])
        if not verifier.is_valid_request(body, headers):
            print("✗ Invalid request signature. Potential security breach!")
            return fastapi.Response(status_code=403)

        # 3. Parse the JSON payload
        payload = json.loads(body)
        print(json.dumps(payload, indent=2))  # Pretty print the payload for debugging

        # 4. Handle Slack's one-time URL verification challenge
        if payload.get("type") == "url_verification":
            return {"challenge": payload.get("challenge")}

        if payload.get("type") == "event_callback" and payload.get("event").get("type") == "app_mention":
            background_tasks.add_task(handle_slack_message, payload.get("event"))

        # 5. Acknowledge all other events for now
        return {"status": "ok"}

    return web_app
