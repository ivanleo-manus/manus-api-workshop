# Manus API Workshop

Welcome to the Manus API workshop. This repository provides a structured, hands-on guide to building complex workflows with the new Manus API.

The workshop is divided into three foundational notebooks and a final capstone project.

1. **API Fundamentals**: This notebook covers the core mechanics of the Manus API. You will learn how to authenticate, create tasks, poll for their status, and interpret the results.

2. **File Handling**: Here you'll learn how to work with files in the Manus API so that your agent has the data it needs to reason effectively.

3. **Webhooks**: Polling doesn't work at scale. Learn why webhooks are a useful tool to implement here which will allow you to listen for task completion events.

4. **Building our Agent**: In the final portion, we'll then integrate all of our concepts together to build a deployable support agent using FastAPI and Modal.

## Setup

> Make sure that you've signed up on [Manus](https://manus.im/app#settings/integrations/api) and obtain an API key. Our documentation is available at [open.manus.ai/docs](https://open.manus.ai/docs).

1. First, install the requirements for this project. We recommend [uv](https://docs.astral.sh/uv/getting-started/installation/) for this tutorial to manage dependencies.

```bash
uv venv
source .venv/bin/activate
uv sync
```

2. Then, make sure that you update the `.env` file with your MANUS_API_KEY.

```
MANUS_API_KEY=<API KEY GOES HERE>
```

## What You'll Build

By the end of this workshop, you'll have put together a simple agent which:

1. Automatically analyzes incoming support tickets
2. Processes user descriptions and screenshots
3. Generates structured reports in your knowledge base

