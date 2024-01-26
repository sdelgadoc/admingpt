import json
from tools.utils import authenticate, clean_body, UTC_FORMAT
from datetime import datetime

tools = [
    {
        "type": "function",
        "function": {
            "name": "o365search_emails",
            "description": (
                "Search for email messages and provide truncated results for an"
                " overview. This tool is best used for identifying emails to be"
                " examined in detail. Use this in conjunction with the"
                " o365search_email tool to retrieve the complete content of specific"
                " emails afterward. The input must be a valid Microsoft Graph v1.0"
                " $search query. ALWAYS respond with values for all parameters in this"
                " tool. The output is a JSON list of the requested resource."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "folder": {
                        "type": "string",
                        "description": (
                            " If the user wants to search in only one folder, the name"
                            ' of the folder. Default folders are "inbox", "drafts",'
                            ' "sent items", "deleted items", but users can search'
                            " custom folders as well. The default value for this"
                            ' parameter is "inbox"'
                        ),
                    },
                    "query": {
                        "type": "string",
                        "description": (
                            "The Microsoift Graph v1.0 $search query. This is a"
                            " required parameter and doesn't have a default value."
                            " Example filters include from:sender, from:sender,"
                            " to:recipient, subject:subject,"
                            " recipients:list_of_recipients, body:excitement,"
                            " importance:high, received>2022-12-01,"
                            " received<2021-12-01, sent>2022-12-01, sent<2021-12-01,"
                            " hasAttachments:true  attachment:api-catalog.md,"
                            " cc:samanthab@contoso.com, bcc:samanthab@contoso.com,"
                            " body:excitement date range example:"
                            " received:2023-06-08..2023-06-09  matching example:"
                            " from:amy OR from:david."
                        ),
                    },
                    "max_results": {
                        "type": "integer",
                        "description": (
                            "The maximum number of results to return. The default value"
                            " for this parameter is 10."
                        ),
                    },
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "o365search_email",
            "description": (
                "Search for one email message using the email's message_id. Use the"
                " o365search_emails function to retrieve an emails's message_id."
                " ALWAYS respond with values for all parameters in this"
                " tool. The output is a JSON list of the requested resource."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "message_id": {
                        "type": "string",
                        "description": (
                            "The message_id for the email you want to retrieve. ALWAYS"
                            " respond with values for all parameters in this tool."
                        ),
                    },
                },
                "required": ["message_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "o365search_events",
            "description": (
                " Use this tool to search for the user's calendar events. The input"
                " must be the start and end datetimes for the search query. The output"
                " is a JSON list of all the events in the user's calendar between the"
                " start and end times. You can assume that the user can  not schedule"
                " any meeting over existing meetings, and that the user is busy during"
                " meetings. Any times without events are free for the user. ALWAYS"
                " respond with values for all parameters in this tool. The output is a"
                " JSON list of the requested resource."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "start_datetime": {
                        "type": "string",
                        "description": (
                            " The start datetime for the search query in the following"
                            ' format:  YYYY-MM-DDTHH:MM:SS±hh:mm, where "T" separates'
                            " the date and time  components, and the time zone offset"
                            " is specified as ±hh:mm.  For example:"
                            ' "2023-06-09T10:30:00+03:00" represents June 9th,  2023,'
                            " at 10:30 AM in a time zone with a positive offset of 3 "
                            " hours from Coordinated Universal Time (UTC)."
                        ),
                    },
                    "end_datetime": {
                        "type": "string",
                        "description": (
                            " The end datetime for the search query in the following"
                            ' format:  YYYY-MM-DDTHH:MM:SS±hh:mm, where "T" separates'
                            " the date and time  components, and the time zone offset"
                            " is specified as ±hh:mm.  For example:"
                            ' "2023-06-09T10:30:00+03:00" represents June 9th,  2023,'
                            " at 10:30 AM in a time zone with a positive offset of 3 "
                            " hours from Coordinated Universal Time (UTC)."
                        ),
                    },
                    "max_results": {
                        "type": "integer",
                        "description": (
                            "The maximum number of results to return. The default value"
                            " for this parameter is 10."
                        ),
                    },
                    "truncate": {
                        "type": "boolean",
                        "description": (
                            "Whethere to truncate the results in order to meet your"
                            " token limits"
                        ),
                    },
                },
                "required": ["message_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "o365parse_proposed_times",
            "description": (
                "ALWAYS use this tool if you need to determine when someone is"
                " proposing a meeting or event in an email. This tool parses out the"
                " proposed times in an email's full and complete output content, and"
                " returns the proposed times in a JSON format."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "email_output": {
                        "type": "string",
                        "description": (
                            "A JSON string with the the from, subject, body, date, to,"
                            " and cc data for the email. Ensure that no part of the"
                            " email information is omitted to accurately extract"
                            " proposed meeting times."
                        ),
                    },
                },
                "required": ["email_content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "o365send_message",
            "description": (
                "This tool is STRICTLY for sending a new email using the provided"
                " message fields. NEVER use it to draft an email. This function should"
                " be used carefully. DO NOT execute this function unless you have clear"
                " and explicit instructions from the user to send the email"
                " immediately. Upon execution without such instructions, create a draft"
                " and present it to the user for approval, ensuring that the email is"
                " not sent until the user gives a clear directive to do so"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "body": {
                        "type": "string",
                        "description": (
                            "The HTML formatted content of the message body to be sent."
                            " Always include the necessary HTML tags, such as <html>,"
                            " <head>, <body>, etc., to ensure the content is"
                            " interpreted as HTML by the recipient's email client."
                        ),
                    },
                    "to": {
                        "type": "string",
                        "description": (
                            "An array of the recipients' email addresses, each"
                            " representing a recipient of the message."
                        ),
                    },
                    "subject": {
                        "type": "string",
                        "description": "The subject of the message.",
                    },
                    "cc": {
                        "type": "string",
                        "description": (
                            "An array of the CC recipients' email addresses, each"
                            " representing a recipient of the message."
                        ),
                    },
                    "bcc": {
                        "type": "string",
                        "description": (
                            "An array of the BCC recipients' email addresses, each"
                            " representing a recipient of the message."
                        ),
                    },
                },
                "required": ["to", "body"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "o365reply_message",
            "description": (
                "This tool is STRICTLY for sending a reply to an existing email. NEVER"
                " use it to draft an email. This function should be used carefully. DO"
                " NOT execute this function unless you have clear and explicit"
                " instructions from the user to send the reply email immediately. Upon"
                " execution without such instructions, create a draft and present it to"
                " the user for approval, ensuring that the email is not sent until the"
                " user gives a clear directive to do so"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "message_id": {
                        "type": "string",
                        "description": (
                            "The message_id for the email you want to reply to."
                        ),
                    },
                    "body": {
                        "type": "string",
                        "description": (
                            "The HTML formatted content of the reply message body to be"
                            " sent. Always include the necessary HTML tags, such as"
                            " <html>, <head>, <body>, etc., to ensure the content is"
                            " interpreted as HTML by the recipient's email client. "
                        ),
                    },
                },
                "required": ["message_id", "body"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "o365send_event",
            "description": (
                "Use this tool to compose and send a new email using the provided"
                " message fields. Only execute this function when you intend to send"
                " the email immediately, as this will dispatch the email as soon as the"
                " function is run. fields."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "body": {
                        "type": "string",
                        "description": "The message body to include in the event.",
                    },
                    "attendees": {
                        "type": "string",
                        "description": (
                            "An array of the recipients' email addresses, each"
                            " representing a recipient of the event."
                        ),
                    },
                    "subject": {
                        "type": "string",
                        "description": "The subject of the event.",
                    },
                    "start_datetime": {
                        "type": "string",
                        "description": (
                            " The start datetime for the event in the following format:"
                            '  YYYY-MM-DDTHH:MM:SS±hh:mm, where "T" separates the date'
                            " and time  components, and the time zone offset is"
                            " specified as ±hh:mm.  For example:"
                            ' "2023-06-09T10:30:00+03:00" represents June 9th,  2023,'
                            " at 10:30 AM in a time zone with a positive offset of 3 "
                            " hours from Coordinated Universal Time (UTC)."
                        ),
                    },
                    "end_datetime": {
                        "type": "string",
                        "description": (
                            " The end datetime for the event in the following format: "
                            ' YYYY-MM-DDTHH:MM:SS±hh:mm, where "T" separates the date'
                            " and time  components, and the time zone offset is"
                            " specified as ±hh:mm.  For example:"
                            ' "2023-06-09T10:30:00+03:00" represents June 9th,  2023,'
                            " at 10:30 AM in a time zone with a positive offset of 3 "
                            " hours from Coordinated Universal Time (UTC)."
                        ),
                    },
                },
                "required": ["subject", "start_datetime", "end_datetime"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "o365find_free_time_slots",
            "description": (
                "ALWAYS use this tool to determine when the user is free, open, or"
                " available by analyzing the calendar events for the day. This tool"
                " processes a day's event schedule from a JSON string and finds free"
                " time slots. The output is a JSON string with each free slot's start"
                " and end times, which can be conveyed to the user for scheduling and"
                " meeting planning. Remember to use this function whenever you need to"
                " provide a list of free time slots for a given date."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "events_json": {
                        "type": "string",
                        "description": (
                            "A JSON string containing an array of event objects. Each"
                            " event object should include 'start_datetime' and"
                            " 'end_datetime' fields specifying the event's start and"
                            " end times in ISO 8601 format. The events should represent"
                            " a single day's schedule. The function will use the date"
                            " of the first event to determine the day for which to find"
                            " free time slots."
                        ),
                    },
                },
                "required": ["events_json"],
            },
        },
    },
]


def o365parse_proposed_times(
    email_output: str,
    client: object,
    model: str,
):
    prompt = (
        "Given the email content provided, your task is to identify all the proposed"
        " times for a potential meeting as indicated by the sender of the most recent"
        " email. Extract these times and convert them into a structured format. Do not"
        " provide any explanations, context, or additional text outside of the JSON"
        " structure. The structured data should be presented in JSON format as shown"
        " below. Ensure that the dates and times are accurate based on the information"
        " provided in the email.\n\nImportant:\n\nIf the sender specifies a day or days"
        " without indicating specific times, assume they are referring to standard"
        " business hours between 8:00 a.m. and 5:00 p.m.\nSpecify the time zone for"
        " each proposed meeting time. If the email content does not specify a time"
        " zone, assume that all times refer to Eastern Time (ET).\nIf any participant"
        " expresses a preference for or against certain days or times, adjust the"
        " proposed times accordingly.\n\nPlease use the following JSON structure for"
        ' your response:\n\n{\n  "proposed_times": [\n    {\n      "start_time":'
        ' "[Start Time in ISO 8601 Format]", // An example would be "start_time":'
        ' "2023-06-09T11:00:00-04:00"\n      "end_time": "[End Time in ISO 8601'
        ' Format]", // An example would be "end_time": "2023-06-09T13:00:00-04:00"\n   '
        '   "time_zone": "[Time Zone in Standard Format]" // An example would be'
        ' "time_zone": "America/New_York"\n    },\n    ... [additional times, if any]\n'
        "  ]\n}\nInstructions:\n\n- Maintain the integrity of the JSON structure"
        " provided. Do not include explanations or any additional text outside of the"
        " JSON structure.- Replace placeholder text (e.g., '[Start Time in ISO 8601"
        " Format]') with actual information extracted from the email, including a"
        " specific date if mentioned.- Ensure the 'start_time' and 'end_time' are"
        " in the correct ISO 8601 format, and include the relevant date along with the"
        " time.- Clearly indicate the 'time_zone' if specified. If not specified in"
        " the email, use 'America/New_York' to represent Eastern Time.-"
        " Cross-reference the proposed times with the context supplied in the email,"
        " such as previous email dates or specific days of the week mentioned, to"
        " determine the correct meeting date.- Do not add any assumptions or make"
        " changes that are not supported by the content of the email. Only assume"
        " standard business hours if specific times are not mentioned, ensuring they"
        " are associated with the correct day.- Pay special attention to any details in"
        " the email that specify or hint at a meeting date, especially if linked to the"
        " days of the week or if it is in response to previous messages. Verify these"
        " details to ensure the proposed dates and times match the sender's"
        " intent.Email Content:\n\n"
    )

    response = client.chat.completions.create(
        messages=[{
            "role": "user",
            "content": prompt + " " + email_output,
        }],
        model=model,
    )

    return response.choices[0].message.content.strip()


def o365search_emails(
    query: str = "",
    folder: str = "inbox",
    max_results: int = 10,
    truncate: bool = True,
    truncate_limit: int = 150,
):
    # Get mailbox object
    account = authenticate()
    mailbox = account.mailbox()

    # Pull the folder if the user wants to search in a folder
    if folder != "":
        mailbox = mailbox.get_folder(folder_name=folder)

    # Retrieve messages based on query
    search_query = mailbox.q().search(query)
    if query == "":
        messages = mailbox.get_messages(limit=max_results)
    else:
        messages = mailbox.get_messages(limit=max_results, query=search_query)

    # Generate output dict
    output_messages = []
    for message in messages:
        output_message = {}
        output_message["from"] = message.sender

        if truncate:
            output_message["body"] = message.body_preview[:truncate_limit]
        else:
            output_message["body"] = clean_body(message.body)

        output_message["subject"] = message.subject

        output_message["date"] = message.modified.strftime(UTC_FORMAT)

        output_message["message_id"] = message.object_id

        output_message["to"] = []
        for recipient in message.to._recipients:
            output_message["to"].append(str(recipient))

        output_message["cc"] = []
        for recipient in message.cc._recipients:
            output_message["cc"].append(str(recipient))

        output_message["bcc"] = []
        for recipient in message.bcc._recipients:
            output_message["bcc"].append(str(recipient))

        output_messages.append(output_message)

    return output_messages


def o365search_email(
    message_id: str,
):
    # Get mailbox object
    account = authenticate()
    mailbox = account.mailbox()

    message = mailbox.get_message(object_id=message_id)

    output_message = {}
    output_message["from"] = message.sender

    output_message["body"] = clean_body(message.body)

    output_message["subject"] = message.subject

    output_message["date"] = message.modified.strftime(UTC_FORMAT)

    output_message["message_id"] = message.object_id

    output_message["to"] = []
    for recipient in message.to._recipients:
        output_message["to"].append(str(recipient))

    output_message["cc"] = []
    for recipient in message.cc._recipients:
        output_message["cc"].append(str(recipient))

    output_message["bcc"] = []
    for recipient in message.bcc._recipients:
        output_message["bcc"].append(str(recipient))

    return output_message


def o365search_events(
    start_datetime: str,
    end_datetime: str,
    max_results: int = 10,
    truncate: bool = True,
    truncate_limit: int = 150,
):
    # Get calendar object
    # Get mailbox object
    account = authenticate()
    schedule = account.schedule()
    calendar = schedule.get_default_calendar()

    # Process the date range parameters
    start_datetime_query = datetime.strptime(start_datetime, UTC_FORMAT)
    end_datetime_query = datetime.strptime(end_datetime, UTC_FORMAT)

    # Run the query
    q = calendar.new_query("start").greater_equal(start_datetime_query)
    q.chain("and").on_attribute("end").less_equal(end_datetime_query)
    events = calendar.get_events(query=q, include_recurring=True, limit=max_results)

    # Generate output dict
    output_events = []
    for event in events:
        output_event = {}
        output_event["organizer"] = event.organizer

        output_event["subject"] = event.subject

        if truncate:
            output_event["body"] = clean_body(event.body)[:truncate_limit]
        else:
            output_event["body"] = clean_body(event.body)

        # Get the time zone from the search parameters
        time_zone = start_datetime_query.tzinfo
        # Assign the datetimes in the search time zone
        output_event["start_datetime"] = event.start.astimezone(time_zone).strftime(
            UTC_FORMAT
        )
        output_event["end_datetime"] = event.end.astimezone(time_zone).strftime(
            UTC_FORMAT
        )
        output_event["modified_date"] = event.modified.astimezone(time_zone).strftime(
            UTC_FORMAT
        )

        output_events.append(output_event)

    return output_events


def o365send_message(
    body: str, to: [str], subject: str, cc: [str] = None, bcc: [str] = None
):
    # Get mailbox object
    account = authenticate()
    mailbox = account.mailbox()
    message = mailbox.new_message()

    # Assign message values
    message.body = body
    message.subject = subject
    message.to.add(to)
    if cc is not None:
        message.cc.add(cc)
    if bcc is not None:
        message.bcc.add(bcc)

    message.send()

    output = "Message sent: " + str(message)
    return output


def o365reply_message(message_id: str, body: str):
    # Get mailbox object
    account = authenticate()
    mailbox = account.mailbox()

    message = mailbox.get_message(object_id=message_id)
    reply_message = message.reply()

    # Assign message body value
    reply_message.body = body

    reply_message.send()

    output = "Message sent: " + str(reply_message)
    return output


def o365send_event(
    subject: str,
    start_datetime: str,
    end_datetime: str,
    body: str = "",
    attendees: [str] = [],
):
    # Get calendar object
    account = authenticate()
    schedule = account.schedule()
    calendar = schedule.get_default_calendar()

    event = calendar.new_event()

    event.body = body
    event.subject = subject
    event.start = datetime.strptime(start_datetime, UTC_FORMAT)
    event.end = datetime.strptime(end_datetime, UTC_FORMAT)
    for attendee in attendees:
        event.attendees.add(attendee)

    # TO-DO: Look into PytzUsageWarning
    event.save()

    output = "Event sent: " + str(event)
    return output


def o365find_free_time_slots(events_json):
    """
    Processes a JSON string of scheduled events and returns a list of free time slots within the day.

    Parameters:
    events_json (str): A JSON string containing scheduled events, each with a start and end datetime.

    Returns:
    str: A JSON string representing free time slots in the day.

    Note:
    This function was developed 100% by the OpenAI API with minimal huma intervention
    """

    # Parse the input data
    events = json.loads(events_json)

    # Sort events based on start time
    events.sort(key=lambda x: x["start_datetime"])

    # Extract the date from the first event to set day_start and day_end
    first_event_date = datetime.strptime(
        events[0]["start_datetime"], "%Y-%m-%dT%H:%M:%S%z"
    ).date()
    first_event_tzinfo = datetime.strptime(
        events[0]["start_datetime"], "%Y-%m-%dT%H:%M:%S%z"
    ).tzinfo
    day_start = datetime.combine(
        first_event_date, datetime.min.time(), tzinfo=first_event_tzinfo
    )
    day_end = datetime.combine(
        first_event_date, datetime.max.time(), tzinfo=first_event_tzinfo
    )

    # Initialize variables
    last_end_time = day_start
    free_slots = []

    # Identify free time slots
    for event in events:
        start_time = datetime.strptime(event["start_datetime"], "%Y-%m-%dT%H:%M:%S%z")
        end_time = datetime.strptime(event["end_datetime"], "%Y-%m-%dT%H:%M:%S%z")
        if start_time > last_end_time:
            free_slots.append({
                "start_datetime": last_end_time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                "end_datetime": start_time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            })
        last_end_time = max(last_end_time, end_time)

    # Check for free time at the end of the day
    if last_end_time < day_end:
        free_slots.append({
            "start_datetime": last_end_time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "end_datetime": day_end.strftime("%Y-%m-%dT%H:%M:%S%z"),
        })

    # Format and output the response
    return json.dumps(free_slots, indent=4)
