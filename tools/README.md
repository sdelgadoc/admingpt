# Office365 Toolkit for the OpenAI API - 💼✉️📅

Welcome to the **Office365 Toolkit**—a robust toolset designed to simplify email, calendar, and scheduling tasks by integrating with the OpenAI API. Automate tasks like parsing emails, detecting free times, and scheduling events directly from your Office365 account.

## Features

- **Email Search**: Find emails using advanced filters like sender, subject, and attachments.
- **Email Parsing**: Extract meeting times from email content for quick scheduling.
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
cd tools
```

## Usage

### 1. Searching Emails
Use `o365search_emails` to search for specific emails.

```python
emails = o365search_emails(query="from:boss@company.com", folder="inbox", max_results=5)
```

### 2. Extracting Proposed Times
Use `o365parse_proposed_times` to parse meeting times from emails.

```python
proposed_times = o365parse_proposed_times(email_output=email_content)
```

### 3. Finding Free Time Slots
Find your availability with `o365find_free_time_slots`.

```python
free_slots = o365find_free_time_slots(
  start_datetime="2024-09-01T08:00:00-05:00", 
  end_datetime="2024-09-01T17:00:00-05:00"
)
```

### 4. Sending Event Invitations
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

### 5. Replying to Emails
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
- **o365parse_proposed_times**: Extract proposed times from emails.
- **o365find_free_time_slots**: Find free calendar slots.
- **o365send_message**: Send or draft new emails.
- **o365reply_message**: Reply to emails or draft replies.
- **o365send_event**: Schedule and send event invitations.

## Contributions

We welcome contributions via issues or pull requests to enhance the toolkit.