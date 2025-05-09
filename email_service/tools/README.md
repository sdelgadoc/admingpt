# Office365 Toolkit for the OpenAI API - 💼✉️📅

Welcome to the **Office365 Toolkit**—a robust toolset designed to simplify email, calendar, and scheduling tasks by integrating with the OpenAI API. Automate tasks like parsing emails, detecting free times, and scheduling events directly from your Office365 account.

## Features

- **Email Search**: Find emails using advanced filters like sender, subject, and attachments.
- **Free Time Detection**: Identify open calendar slots for efficient planning.
- **Event Scheduling**: Automatically send meeting invites based on extracted times.
- **Email Reply Automation**: Create and send replies directly from the toolkit.

## Why Use This Toolkit?

Eliminate the hassle of managing emails and meetings. The toolkit automates scheduling, free time detection, and email interactions, streamlining your workflow.

## Installation

Clone the repository and install the dependencies:

```bash
git clone https://github.com/sdelgadoc/AdminGPT.git
cd AdminGPT
pip install -r requirements.txt
cd admingpt_project/email_serivce/tools
```

## Authentication: Generate your Microsoft Graph credentials
To use this toolkit, you need to set up your credentials explained in the [Microsoft Graph authentication and authorization overview](https://learn.microsoft.com/en-us/graph/auth/). Once you've received a CLIENT_ID and CLIENT_SECRET, you can input them as environmental variables below. You can also use the authentication instructions from the [O365 Python library documentation](https://o365.github.io/python-o365/latest/getting_started.html#oauth-setup-pre-requisite).

## Usage Examples

### 1. Searching Emails
Use `o365search_emails` to search for specific emails.

```python
emails = o365search_emails(query="from:boss@company.com", folder="inbox", max_results=5)
```

### 2. Finding Free Time Slots
Find your availability with `o365find_free_time_slots`.

```python
free_slots = o365find_free_time_slots(
  start_datetime="2024-09-01T08:00:00-05:00", 
  end_datetime="2024-09-01T17:00:00-05:00"
)
```

### 3. Sending Event Invitations
Send invites using `o365send_event`.

```python
o365send_event(
    subject="Team Meeting",
    start_datetime="2024-09-01T10:00:00-05:00",
    end_datetime="2024-09-01T11:00:00-05:00",
    attendees=["colleague1@company.com"],
    body="Project discussion."
)
```

### 4. Replying to Emails
Reply to emails with `o365reply_message`.

```python
reply = o365reply_message(
    message_id="AAMkADk7M...",
    body="<p>Hi,</p><p>Thanks!</p><p>Best,</p>",
    create_draft=True
)
```

## Available Functions

- **o365search_emails**: Search emails with custom queries.
- **o365search_email**: Retrieve full email content by message ID.
- **o365find_free_time_slots**: Find free calendar slots.
- **o365send_message**: Send or draft new emails.
- **o365reply_message**: Reply to emails or draft replies.
- **o365send_event**: Schedule and send event invitations.

## Contributions

We welcome contributions via issues or pull requests to enhance the toolkit.