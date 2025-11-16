# Manus API Workshop: Building Event-Driven AI Workflows with Webhooks

A comprehensive 90-minute workshop that teaches developers how to build production-ready, event-driven AI workflows using the Manus API.

## Workshop Overview

This workshop addresses a critical challenge in modern AI development: **managing long-running asynchronous AI tasks in production systems**. You'll learn how to leverage the Manus API's webhook system to build scalable, event-driven workflows that don't block your application.

### What You'll Learn

By the end of this workshop, you will be able to:

- Create and manage AI tasks using the Manus API
- Upload and attach files to tasks for document processing
- Implement polling strategies for task completion
- Set up webhooks for event-driven notifications
- Handle different task lifecycle events
- Build a complete notification pipeline
- Apply production-ready patterns to your own projects

### Prerequisites

- Basic Python programming knowledge
- Understanding of REST APIs
- Familiarity with asynchronous programming concepts (helpful but not required)
- A Manus account with API access

### Workshop Duration

**Total Time**: 90 minutes

- Part 1: Foundation (20 minutes)
- Part 2: Core Workflow (30 minutes)
- Part 3: Event-Driven Architecture (25 minutes)
- Part 4: Real-World Application (10 minutes)
- Part 5: Q&A (5 minutes)

## Repository Structure

```
manus-api-webhook-workshop/
├── 01-basics/                  # Part 1: Getting started with Manus API
│   ├── starter.py             # Starter template
│   ├── solution.py            # Complete solution
│   └── README.md              # Section guide
├── 02-file-handling/          # Part 2: Working with files
│   ├── starter.py
│   ├── solution.py
│   ├── sample-document.pdf    # Sample file for testing
│   └── README.md
├── 03-webhooks/               # Part 3: Implementing webhooks
│   ├── starter.py
│   ├── solution.py
│   ├── webhook-handler.py     # Flask webhook endpoint
│   └── README.md
├── 04-complete-workflow/      # Part 4: End-to-end example
│   ├── workflow.py            # Complete workflow implementation
│   ├── config.py              # Configuration management
│   └── README.md
├── docs/                      # Additional documentation
│   ├── setup-guide.md         # Environment setup instructions
│   ├── api-reference.md       # Quick API reference
│   └── troubleshooting.md     # Common issues and solutions
├── slides/                    # Workshop presentation materials
│   └── workshop-slides.md     # Slide content in markdown
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/manus-api-webhook-workshop.git
cd manus-api-webhook-workshop
```

### 2. Set Up Your Environment

```bash
# Create a virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Your API Key

Create a `.env` file in the root directory:

```bash
MANUS_API_KEY=your-api-key-here
```

Get your API key from the [Manus API Integration settings](https://manus.im/settings/api).

### 4. Verify Your Setup

```bash
cd 01-basics
python solution.py
```

If everything is configured correctly, you should see a task created successfully.

## Workshop Sections

### Part 1: Foundation (01-basics/)

Learn the fundamentals of the Manus API:
- Authentication and API key setup
- Creating your first task
- Understanding task statuses (running, pending, completed, error)
- Retrieving task results

**Time**: 20 minutes

### Part 2: Core Workflow (02-file-handling/)

Master file handling and task management:
- Uploading files to Manus
- Attaching files to tasks
- Polling for task completion
- Handling different output types
- Multi-turn conversations

**Time**: 30 minutes

### Part 3: Event-Driven Architecture (03-webhooks/)

Implement webhooks for production systems:
- Why webhooks beat polling
- Setting up webhook endpoints
- Registering webhooks via API
- Understanding webhook payloads
- Handling task_created and task_stopped events
- Building notification systems

**Time**: 25 minutes

### Part 4: Real-World Application (04-complete-workflow/)

Put it all together:
- Complete workflow from creation to notification
- Production best practices
- Error handling and retry logic
- Security considerations
- Use case examples

**Time**: 10 minutes

## Key Concepts

### Task Lifecycle

Tasks in Manus go through several states:

1. **running**: The agent is actively working on your request
2. **pending**: The agent needs user input to continue
3. **completed**: The task finished successfully
4. **error**: The task encountered an error

### Webhook Events

The Manus API sends two types of webhook events:

1. **task_created**: Triggered immediately after task creation
2. **task_stopped**: Triggered when a task completes or needs input
   - `stop_reason: "finish"` - Task completed successfully
   - `stop_reason: "ask"` - Task needs user input

### Polling vs Webhooks

**Polling** (checking status repeatedly):
- Simple to implement
- Good for development and testing
- Inefficient for production (wastes resources)

**Webhooks** (event-driven notifications):
- More complex initial setup
- Ideal for production systems
- Efficient and scalable
- Real-time notifications

## Use Cases

This workshop teaches patterns applicable to:

- **Document Processing Pipeline**: Upload documents, extract insights, notify when complete
- **Automated Research Assistant**: Trigger research tasks, receive results via webhook
- **Email Triage System**: Process emails with AI, route based on results
- **Content Generation Workflow**: Create content, review via webhook notification
- **Data Analysis Pipeline**: Submit analysis tasks, get notified with visualizations

## Additional Resources

- [Manus API Documentation](https://open.manus.ai/docs)
- [Webhook Best Practices](./docs/troubleshooting.md)
- [API Reference Quick Guide](./docs/api-reference.md)
- [Setup Troubleshooting](./docs/troubleshooting.md)

## Support

If you encounter issues during the workshop:

1. Check the [troubleshooting guide](./docs/troubleshooting.md)
2. Review the solution code in each section
3. Ask questions during the Q&A session
4. Visit [Manus Help Center](https://help.manus.im)

## Contributing

Found an issue or have a suggestion? Please open an issue or submit a pull request.

## License

This workshop material is provided under the MIT License. See LICENSE file for details.

## Acknowledgments

Created for the Manus API Workshop Series. Special thanks to the Manus team for their comprehensive API documentation and support.

---

**Ready to get started?** Head to [01-basics/](./01-basics/) to begin the workshop!
