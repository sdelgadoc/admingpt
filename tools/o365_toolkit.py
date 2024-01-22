from tools.utils import authenticate, clean_body, UTC_FORMAT
from datetime import datetime as dt

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
                            "A string with the full and complete output of the email"
                            " including the from, subject, body, date, to, and cc data."
                            " Ensure that no part of the email information is omitted"
                            " to accurately extract proposed meeting times."
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
                "Use this tool to send an email with the provided message fields."
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
                "Use this tool to send a reply to an existing email using the provided"
                " message fields. This function should only be executed when you are"
                " certain you want to send the reply email, as it will send the reply"
                " immediately upon execution"
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
]


def o365parse_proposed_times(
    email_output: str,
    client: object,
    model: str,
):
    prompt = (
        "Given the email content provided, your task is to identify all the "
        "proposed times for a potential meeting as indicated by the sender of "
        "the most recent email. Extract these times and convert them into a "
        "structured format. Do not provide any explanations, context, or "
        "additional text outside of the JSON structure. The structured data "
        "should be presented in JSON format as shown below. Ensure that the "
        "dates and times are accurate based on the information provided in the "
        "email.\n\n"
        "Important:\n\n"
        "If the sender specifies a day or days without indicating specific "
        "times, assume they are referring to standard business hours between "
        "8:00 a.m. and 5:00 p.m.\n"
        "Specify the time zone for each proposed meeting time. If the email "
        "content does not specify a time zone, assume that all times refer to "
        "Eastern Time (ET).\n"
        "If any participant expresses a preference for or against certain days "
        "or times, adjust the proposed times accordingly.\n\n"
        "Please use the following JSON structure for your response:\n\n"
        "{\n"
        '  "proposed_times": [\n'
        "    {\n"
        '      "start_time": "[Start Time in ISO 8601 Format]", // An example '
        'would be "start_time": "2023-06-09T11:00:00-04:00"\n'
        '      "end_time": "[End Time in ISO 8601 Format]", // An example '
        'would be "end_time": "2023-06-09T13:00:00-04:00"\n'
        '      "time_zone": "[Time Zone in Standard Format]" // An example '
        'would be "time_zone": "America/New_York"\n'
        "    },\n"
        "    ... [additional times, if any]\n"
        "  ]\n"
        "}\n"
        "Instructions:\n\n"
        "Maintain the integrity of the JSON structure provided. Do not include "
        "explanations or any additional text outside of the JSON structure.\n"
        'Replace placeholder text (e.g., "[Start Time in ISO 8601 Format]") '
        "with actual information extracted from the email.\n"
        'Ensure the "start_time" and "end_time" are in the correct ISO 8601 '
        'format, and the "time_zone" is clearly indicated. If not specified '
        'in the email, use "America/New_York" to represent Eastern Time.\n'
        "Do not add any assumptions or make changes that are not supported by "
        "the content of the email. Only assume standard business hours if "
        "specific times are not mentioned.\n\n"
        "Email Content:\n\n"
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
    start_datetime_query = dt.strptime(start_datetime, UTC_FORMAT)
    end_datetime_query = dt.strptime(end_datetime, UTC_FORMAT)

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
    event.start = dt.strptime(start_datetime, UTC_FORMAT)
    event.end = dt.strptime(end_datetime, UTC_FORMAT)
    for attendee in attendees:
        event.attendees.add(attendee)

    # TO-DO: Look into PytzUsageWarning
    event.save()

    output = "Event sent: " + str(event)
    return output
