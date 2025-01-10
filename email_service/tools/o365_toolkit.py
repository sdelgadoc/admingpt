import json, openai
from .utils import authenticate, clean_body, UTC_FORMAT
from datetime import datetime
from zoneinfo import ZoneInfo
from pydantic import BaseModel, Field
from typing import List

toolkit_prompt = """
1. If you need to extract times from an email or message follow these steps:
    1.1 DO NOT use the 'o365search_emails' or 'o365search_email' functions to find emails, the email content is in my message to you.
    1.2 If I reference an email, extract proposed times from the most recent email sender, ensuring accuracy and correct time zones.
        1.2.1 If availability is given for a full day without specific times, assume business hours (08:00:00 to 17:00:00) in their local time zone.
        1.2.2 For before or after a certain time, also assume the unspecified times fall within business hours (08:00:00 to 17:00:00).
        1.2.3 If a meeting length is not specified, assume a 1 hour meeting.
        1.2.4 Only consider specific times proposed by the most recent email sender when extracting time ranges.
2. If I ask you whether I am free at the times proposed by me or in an email:
    2.1 Extract the times by following all the steps listed under section 1, including any substeps.
    2.2 Once you have the start and end datetimes, call the 'o365find_free_time_slots' functions once for each set of proposed times to find the times that are free on my calendar.
    2.3 Only return the business hours where I am free.
3. If I ask you to retrieve or perform a task on someone's most recent email:
    2.1 Use the 'o365search_emails' funtion to find the 5 most recent emails from the person, and extract the email's 'message_id'.
    2.2 Use the 'o365search_email' function with the correct 'message_id' to extract the email's full content.
4. If I ask you to send an invitation or invite for a time proposed by me or in an email:
    4.1 Extract the times by following all the steps listed under section 1, including any substeps.
    4.2 Extract the attendees to the event from my request and any email information.
    4.3 Call the 'o365send_event' function with the extracted times, extracted attendees, and a relevant subject to send the invivation for the event.
5. If I ask you to organize a meeting or a call for a time proposed by me or in an email:
    5.1 Extract the times by following all the steps listed under section 1, including any substeps.
    5.2 Check whether I am free at the times you extracted by following all the steps listed under section 2, including any substeps.
    5.3 If I am free at the extracted times:
        5.3.1 Create an event at the earliest proposed time by following all the steps listed under section 4, including any substeps.
    5.4 If I am not free at the extracted times:
        5.4.1 Return the times I am free during business hours on two consecutive business days starting on the same day as the earliest proposed time by following all the steps listed under section 2, including any substeps.
6. If I ask you to reply or respond to an email or to a person who sent an email, which I am including in my email to you:
    6.1 ALWAYS follow steps 6.2, 6.3, 6.4, and 6.5 to respond to the forwarded email, and NEVER skip steps 6.2, 6.3, 6.4, and 6.5 to respond to the email by me.
	6.2 Extract the content of the forwarded email first.
		6.2.1 Search for the forwarded message content by identifying "Forwarded message" or "From" lines within the email body.
        6.2.2 The forwarded message will be immediately after the message I sent you.
		6.2.2 Always prioritize the forwarded email content over the most recent one in the chain.
	6.3 Once the forwarded email is identified, extract its sender and subject and use the 'o365search_emails' function to locate the original email.
    6.4 With the full email and the email's 'message_id' reply using the 'o365reply_message' function.
"""

### START TOOL PROTOTYPES HERE
o365search_emails_description = (
    "Use this function to quickly identify recent or relevant emails based"
    " on specific query criteria. It provides an overview of multiple"
    " emails, including truncated contents. Ideal for initial searches when"
    " you need to locate one or more emails quickly."
)


class O365SearchEmailsParameters(BaseModel):
    query: str = Field(
        ...,
        description="The Microsoift Graph v1.0 $search query. This is a "
        ' required parameter. Ensure that the query does not contain double quotes (") around any of the search parameters.'
        " Example filters include from:sender, from:sender,"
        " to:recipient, subject:subject,"
        " recipients:list_of_recipients, body:excitement,"
        " importance:high, received>2022-12-01,"
        " received<2021-12-01, sent>2022-12-01, sent<2021-12-01,"
        " hasAttachments:true  attachment:api-catalog.md,"
        " cc:samanthab@contoso.com, bcc:samanthab@contoso.com,"
        " body:excitement date range example:"
        " received:2023-06-08..2023-06-09  matching example:"
        ' from:amy OR from:david. Avoid using: from:"firstnamelastname@company.com" subject:"Email Topic"',
    )
    folder: str = Field(
        ...,
        description=" If the user wants to search in only one folder, the name"
        ' of the folder. Possible folders are "inbox", "drafts",'
        ' "sent items", "deleted items", but users can search'
        ' custom folders as well. The default value for this parameter is "inbox".',
    )
    max_results: int = Field(
        ...,
        description="The maximum number of results to return. The default value for this parameter is 10.",
    )


o365search_email_description = (
    "Use this function when you need to retrieve the full and detailed"
    " content of a specific email, identified by its `message_id`. This is"
    " essential when complete information is required for thorough"
    " analysis, as in the case of identifying proposed meeting times,"
    " reading complete attachments, or understanding the full context of"
    " the email. Employ this function after identifying the email of"
    " interest using the o365search_emails function."
)


class O365SearchEmailParameters(BaseModel):
    message_id: str = Field(
        ...,
        description="The message_id for the email you want to retrieve from the o365search_emails function.",
    )


o365parse_proposed_times_description = (
    "ALWAYS use this tool if you need to determine when someone is"
    " proposing a meeting or event in an email. This tool parses out the"
    " proposed times in an email's full and complete output content, and"
    " returns the proposed times in a JSON format."
)


class O365ProposedTimesParameters(BaseModel):
    email_output: str = Field(
        ...,
        description=" All the data including the from, subject, body, date, to,"
        " and cc data for the email. Ensure that no part of the"
        " email information is omitted to accurately extract"
        " proposed meeting times.",
    )


o365find_free_time_slots_description = (
    "ALWAYS use this tool to determine when the user is free, open, or"
    " available by analyzing the calendar events between a start and end datetime. This tool"
    " accepts a start and end datetime for which you want to know if I am free. The output is a list of event with each free"
    " slot's start and end times, which can be conveyed to the user for scheduling and meeting planning."
)


class O365FindFreeTimeSlotsParameters(BaseModel):
    start_datetime: str = Field(
        ...,
        description="Start time of the search query in ISO 8601 format (e.g., '2022-03-28T15:00:00-04:00').",
    )
    end_datetime: str = Field(
        ...,
        description="End time of the search query in ISO 8601 format (e.g., '2022-03-28T15:00:00-04:00').",
    )


o365search_events_description = (
    " Use this tool to search for the user's calendar events. The input"
    " must be the start and end datetimes for the search query in ISO 8601 format with the correct UTC offset. The output"
    " is a JSON list of all the events in the user's calendar between the"
    " start and end times. You can assume that the user can  not schedule"
    " any meeting over existing meetings, and that the user is busy during"
    " meetings. Any times without events are free for the user. ALWAYS"
    " respond with values for all parameters in this tool."
)


class O365SearchEventsParameters(BaseModel):
    start_datetime: str = Field(
        ...,
        description="Start time of the search query in ISO 8601 format (e.g., '2022-03-28T15:00:00-04:00').",
    )
    end_datetime: str = Field(
        ...,
        description="End time of the search query in ISO 8601 format (e.g., '2022-03-28T15:00:00-04:00').",
    )
    max_results: int = Field(
        ...,
        description="The maximum number of results to return. The default value for this parameter is 10.",
    )
    truncate: bool = Field(
        ...,
        description="Whethere to truncate the results to reduce the size of the response.",
    )


o365reply_message_description = (
    "This function replies or creates reply drafts to existing emails. Do"
    " not reply to an email unless the user gives a clear directive to do"
    " so. The function can either send emails immediately or create drafts"
    " for later review, based on a boolean parameter."
)


class O365ReplyMesssageParameters(BaseModel):
    message_id: str = Field(
        ...,
        description="The message_id for the email you want to reply to.",
    )
    body: str = Field(
        ...,
        description="The HTML formatted content of the message body to be sent."
        " Ensure that paragraphs are separated by additional blank"
        " lines for enhanced readability and visual appeal. Use"
        " `<p></p>` tags for each paragraph and insert `<br>` tags"
        " in between paragraphs to create the desired spacing. For"
        " example: `<p>Hi [Recipient],</p><p>This is the"
        " first line or paragraph.</p><p>This is the last"
        " line or"
        " paragraph.</p><br><pBest,</p><p>[Your Name]</p><br>'",
    )
    create_draft: bool = Field(
        ...,
        description="A boolean parameter (true/false). If set to `true`, the"
        " function creates an email draft that can be reviewed by"
        " the user without sending. If set to `false`, or is"
        " omitted, the email is sent immediately upon executing the"
        " function.",
    )


o365send_message_description = (
    "This function sends or creates drafts of new emails. Do not send an"
    " email unless the user gives a clear directive to do so. The function"
    " can either send emails immediately or create drafts for later review,"
    " based on a boolean parameter."
)


class O365SendMesssageParameters(BaseModel):
    body: str = Field(
        ...,
        description="The HTML formatted content of the message body to be sent."
        " Ensure that paragraphs are separated by additional blank"
        " lines for enhanced readability and visual appeal. Use"
        " `<p></p>` tags for each paragraph and insert `<br>` tags"
        " in between paragraphs to create the desired spacing. For"
        " example: `<p>Hi [Recipient],</p><p>This is the"
        " first line or paragraph.</p><p>This is the last"
        " line or"
        " paragraph.</p><br><pBest,</p><p>[Your Name]</p><br>'",
    )
    to: List[str] = Field(
        ...,
        description="An list of the recipients' email addresses, each"
        " representing a recipient of the message.",
    )
    subject: str = Field(
        ...,
        description="The subject of the message.",
    )
    cc: List[str] = Field(
        ...,
        description="A list of the CC recipients' email addresses, each"
        " representing a recipient of the message.",
    )
    bcc: List[str] = Field(
        ...,
        description="A list of the BCC recipients' email addresses, each"
        " representing a recipient of the message.",
    )
    create_draft: bool = Field(
        ...,
        description="A boolean parameter (true/false). If set to `true`, the"
        " function creates an email draft that can be reviewed by"
        " the user without sending. If set to `false`, or is"
        " omitted, the email is sent immediately upon executing the"
        " function.",
    )


o365send_event_description = (
    "This function sends a new event. Do not send an"
    " event unless the user gives a clear directive to do so."
)


class O365SendEventParameters(BaseModel):
    body: str = Field(
        ...,
        description="The message body to include in the event.",
    )
    attendees: List[str] = Field(
        ...,
        description="A list of the recipients' email addresses, each"
        " representing a recipient of the message.",
    )
    subject: str = Field(
        ...,
        description="The subject of the event.",
    )
    start_datetime: str = Field(
        ...,
        description=" The start datetime for the event in the following format:"
        '  YYYY-MM-DDTHH:MM:SS±hh:mm, where "T" separates the date'
        " and time  components, and the time zone offset is"
        " specified as ±hh:mm.  For example:"
        ' "2023-06-09T10:30:00+03:00" represents June 9th,  2023,'
        " at 10:30 AM in a time zone with a positive offset of 3 "
        " hours from Coordinated Universal Time (UTC).",
    )
    end_datetime: str = Field(
        ...,
        description=" The end datetime for the event in the following format:"
        '  YYYY-MM-DDTHH:MM:SS±hh:mm, where "T" separates the date'
        " and time  components, and the time zone offset is"
        " specified as ±hh:mm.  For example:"
        ' "2023-06-09T10:30:00+03:00" represents June 9th,  2023,'
        " at 10:30 AM in a time zone with a positive offset of 3 "
        " hours from Coordinated Universal Time (UTC).",
    )


### END TOOL PROTOTYPES HERE


tools = [
    openai.pydantic_function_tool(
        O365SearchEmailsParameters,
        name="o365search_emails",
        description=o365search_emails_description,
    ),
    openai.pydantic_function_tool(
        O365SearchEmailParameters,
        name="o365search_email",
        description=o365search_email_description,
    ),
    openai.pydantic_function_tool(
        O365FindFreeTimeSlotsParameters,
        name="o365find_free_time_slots",
        description=o365find_free_time_slots_description,
    ),
    openai.pydantic_function_tool(
        O365SearchEventsParameters,
        name="o365search_events",
        description=o365search_events_description,
    ),
    openai.pydantic_function_tool(
        O365ReplyMesssageParameters,
        name="o365reply_message",
        description=o365reply_message_description,
    ),
    openai.pydantic_function_tool(
        O365SendMesssageParameters,
        name="o365send_message",
        description=o365send_message_description,
    ),
    openai.pydantic_function_tool(
        O365SendEventParameters,
        name="o365send_event",
        description=o365send_event_description,
    ),
]


def o365search_emails(
    query: str = "",
    folder: str = "inbox",
    max_results: int = 10,
    truncate: bool = True,
    truncate_limit: int = 150,
    interface="cli",
):
    # Get mailbox object
    account = authenticate(interface)
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


def o365search_email(message_id: str, interface: str = "cli"):
    # Get mailbox object
    account = authenticate(interface)
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


def o365find_free_time_slots(start_datetime, end_datetime):
    """
    Identifies and returns a list of available free time slots within a specified date and time range.

    Parameters:
    start_datetime (str): A string in ISO 8601 format "YYYY-MM-DDTHH:MM:SS±HH:MM" representing the start of the time range.
    end_datetime (str): A string in ISO 8601 format "YYYY-MM-DDTHH:MM:SS±HH:MM" representing the end of the time range.

    Returns:
    str: A JSON string representing a list of free time slots within the specified range. Each slot includes a start_datetime and end_datetime.
         If there are no free time slots, returns a message indicating that there are no available free times.
    """

    events = o365search_events(start_datetime, end_datetime)

    if not events:
        # If there are no events, return the entire time
        return json.dumps(
            [{"start_datetime": start_datetime, "end_datetime": end_datetime}], indent=4
        )

    # Sort events based on start time
    events.sort(key=lambda x: x["start_datetime"])

    # Set day start and end times
    day_start = datetime.strptime(start_datetime, "%Y-%m-%dT%H:%M:%S%z")
    day_end = datetime.strptime(end_datetime, "%Y-%m-%dT%H:%M:%S%z")

    # Initialize variables
    last_end_time = day_start
    free_slots = []

    # Identify free time slots
    for event in events:
        start_time = datetime.strptime(event["start_datetime"], "%Y-%m-%dT%H:%M:%S%z")
        end_time = datetime.strptime(event["end_datetime"], "%Y-%m-%dT%H:%M:%S%z")

        if start_time > last_end_time:
            free_slots.append(
                {
                    "start_datetime": last_end_time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                    "end_datetime": start_time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                }
            )

        last_end_time = max(last_end_time, end_time)

    # Check for free time at the end of the day
    if last_end_time < day_end:
        free_slots.append(
            {
                "start_datetime": last_end_time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                "end_datetime": day_end.strftime("%Y-%m-%dT%H:%M:%S%z"),
            }
        )

    # Format and output the response
    if free_slots == []:
        return "There are no free times for this search"
    else:
        return json.dumps(free_slots, indent=4)


def o365search_events(
    start_datetime: str,
    end_datetime: str,
    max_results: int = 10,
    truncate: bool = True,
    truncate_limit: int = 150,
    interface: str = "cli",
):
    # Get calendar object
    # Get mailbox object
    account = authenticate(interface)
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


def o365reply_message(
    message_id: str,
    body: str,
    create_draft: bool = False,
    interface: str = "cli",
    reply_to_sender=False,
):
    # Get mailbox object
    account = authenticate(interface)
    mailbox = account.mailbox()

    message = mailbox.get_message(object_id=message_id)
    reply_message = message.reply()

    # Assign message body value
    reply_message.body = body
    # Override 'to' field to the sender if necessary
    if reply_to_sender:
        reply_message.to.add(reply_message.sender)

    if create_draft:
        reply_message.save_draft()
        output = "Draft saved: " + str(message)
    else:
        reply_message.send()
        output = "Message sent: " + str(message)

    return output


def o365send_message(
    body: str,
    to: List[str],
    subject: str,
    cc: List[str] = None,
    bcc: List[str] = None,
    create_draft: bool = False,
    interface: str = "cli",
):
    # Get mailbox object
    account = authenticate(interface)
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

    if create_draft:
        message.save_draft()
        output = "Draft saved: " + str(message)
    else:
        message.send()
        output = "Message sent: " + str(message)

    return output


def o365send_event(
    subject: str,
    start_datetime: str,
    end_datetime: str,
    body: str = "",
    attendees: List[str] = [],
    interface: str = "cli",
):
    # Get calendar object
    account = authenticate(interface)
    schedule = account.schedule()
    calendar = schedule.get_default_calendar()

    event = calendar.new_event()

    event.body = body
    event.subject = subject
    # Parse the start time string into a datetime object with time zone information
    dt = datetime.strptime(start_datetime, UTC_FORMAT)
    # Convert the start time to UTC
    event.start = dt.astimezone(ZoneInfo("America/New_York"))
    # Do the same for event.end
    dt = datetime.strptime(end_datetime, UTC_FORMAT)
    event.end = dt.astimezone(ZoneInfo("America/New_York"))

    for attendee in attendees:
        event.attendees.add(attendee)

    event.save()

    output = "Event sent: " + str(event)
    return output


def o365delete_message(message_id: str, interface: str = "cli"):
    """
    Deletes a specified email message using the provided message_id.

    Parameters:
    message_id (str): The ID of the message to be deleted.
    interface (str): Specifies the interface used for authentication (default is "cli").

    Returns:
    str: A confirmation message indicating the result of the delete action.
    """

    # Get mailbox object
    account = authenticate(interface)
    mailbox = account.mailbox()

    # Retrieve the message
    message = mailbox.get_message(object_id=message_id)

    # Delete the message
    if message:
        message.delete()
        output = f"Message with ID {message_id} has been deleted."
    else:
        output = f"Message with ID {message_id} not found."

    return output
