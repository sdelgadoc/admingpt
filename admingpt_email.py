import os
from utils import (
    create_client,
    run_prompt,
    poll_for_response,
)
from tools.utils import authenticate
from datetime import datetime as dt
from openai import OpenAI
from tools.o365_toolkit import (
    tools,
    toolkit_prompt,
    o365search_emails,
    o365search_email,
    o365reply_message,
)

## Assign environmental files
# Set your OpenAI API key
os.environ["OPENAI_API_KEY"] = "YOUR OPENAI KEY"
# Set your Microsoft Graph client ID
os.environ["CLIENT_ID"] = "YOUR CLIENT ID"
# Set your Microsoft Graph client secret
os.environ["CLIENT_SECRET"] = "YOUR CLIENT SECRET"
# Set global variables
assistant_name = "Monica A. Ingenio"
assistant_first_name = "Monica"
current_date = dt.now()
formatted_date = current_date.strftime("%A, %B %d, %Y")
openai_api_key = os.environ.get("OPENAI_API_KEY")


def create_client(debug=False, model=None, interface="cli"):
    # Retrieve user information
    account = authenticate(interface=interface)
    mailbox = account.mailbox()
    mailboxsettings = mailbox.get_settings()
    timezone = mailboxsettings.timezone
    directory = account.directory(resource="me")
    user = directory.get_current_user()
    client_name = user.full_name
    client_email = user.mail

    # Set values for global variables
    assistant_instructions = (
        "You are an AI Administrative Assistant called "
        + assistant_name
        + ", and I am your executive. My name is "
        + client_name
        + ". My email is "
        + client_email
        + ", and I am in the "
        + timezone
        + " timezone. Today is "
        + formatted_date
        + "."
        + "My business hours are between '8:00 a.m.' and '5:30 a.m.' of my time zone. "
        + "I am not free outside these times, and don't recomment times "
        + "outside these business hours. I will send you requests in "
        + "an email that start wit the phrase 'Hi Monica, '."
        + "Always respond to my requests either with the answer, or a description of the task you performed after you performed it."
        + "Ensure that your responses are in valid HTML and paragraphs are separated "
        + "by additional blank lines for enhanced readability and visual appeal. "
        + "DO NOT EVER use the following tags '```html' [HTML] '```' and ONLY repond with valid HTML."
        + "Use `<br>` tags for each paragraph and to create the desired spacing. For"
        + "example: `Hi [Recipient],<br><br>This is the"
        + "first line or paragraph.<br>"
        + "This is information in bullet form:<ul><li>First bullet</li><li>Second bullet</li>"
        + "<li>Third bullet</li></ul><br>This is the last line or paragraph with a <b>bolded<b> word for emphasis."
        + "<br><br><br>Best,<br><br>Monica A. Ingenio<br><i>(OpenAI-Powered Assistant in Beta, "
        + "please excuse any mistakes)</i><br><br>'\n\n"
        + toolkit_prompt
    )

    # Add the debug prompt if user runs with debug
    if debug:
        debug_prompt = (
            "Please remember to track and document all interactions using the following"
            " format.\n "
            + "Start of Interaction: Briefly note the request. Follow these steps:\n"
            + "Prompt: Briefly describe the user request.\nTool Call: List the function"
            " used and key parameters.\n"
            + "Result: Summarize the result or action taken.\n"
            + "Repeat as needed for each step in the interaction. Conclude with any"
            " noteworthy observations.\n"
            + "End of Interaction\nIf I request a compilation of these interactions,"
            " ensure you're able to share"
            + " the documented interaction logs accurately and comprehensively,"
            " adhering to the detailed format I shared with you."
        )
        # Use the following prompt to retrieve interactions for debugging:
        # Can you please provide the documentation for all the (or specify a particular) interaction following the detailed format we established?
    else:
        debug_prompt = ""
    assistant_instructions += debug_prompt

    client = OpenAI(
        api_key=openai_api_key,
    )

    assistant = client.beta.assistants.create(
        name="AI Administrative Assistant",
        instructions=assistant_instructions,
        model=model,
        tools=tools,
    )

    thread = client.beta.threads.create()

    return client, assistant, thread


def get_prompt_email():

    # Get the user's email
    account = authenticate(interface="cli")
    directory = account.directory(resource="me")
    user = directory.get_current_user()
    client_email = user.mail

    query = (
        "from:"
        + client_email
        + " to:"
        + client_email
        + ' Hi '
        + assistant_first_name
    )

    events = o365search_emails(query, "inbox", 5)

    # Sort events based on start time
    events.sort(key=lambda x: x["date"], reverse=True)

    # Find full email and return it
    message_id = events[0]["message_id"]
    event = o365search_email(message_id)

    return str(event), message_id


# Assign constants
model = "gpt-4o-2024-08-06"

prompt, message_id = get_prompt_email()

(client, assistant, thread) = create_client(model=model)
run = run_prompt(prompt, client, assistant, thread)
response = poll_for_response(client, thread, run, model)

print(response)

response = o365reply_message(
    message_id,
    response,
    interface="cli",
    reply_to_sender=True,
)
