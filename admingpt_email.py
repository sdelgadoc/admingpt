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

    emails = o365search_emails(query, "inbox", 5)

    # Sort emails based on start time
    emails.sort(key=lambda x: x["date"], reverse=True)

    # Find full email and return it
    message_id = emails[0]["message_id"]
    event = o365search_email(message_id)

    return str(event), message_id


# Assign constants
model = "gpt-4o-2024-08-06"

prompt, message_id = get_prompt_email()

(client, assistant, thread) = create_client(debug=False, model=model, interface="email",)
run = run_prompt(prompt, client, assistant, thread)
response = poll_for_response(client, thread, run, model)

response = o365reply_message(
    message_id,
    response,
    interface="cli",
    reply_to_sender=True,
)

print(response)
