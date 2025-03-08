import os, pprint, json, time
from datetime import datetime as dt
from openai import OpenAI
from .tools.o365_toolkit import (
    o365search_emails,
    o365search_email,
    o365search_events,
    o365send_message,
    o365reply_message,
    o365send_event,
    o365find_free_time_slots,
    tools,
    toolkit_prompt,
)
from .tools.utils import authenticate

assistant_first_name = "Monica"
assistant_last_name = "Ingenio"
assistant_name = assistant_first_name + " A. " + assistant_last_name
business_hours = "(09:00:00 to 17:00:00)"


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
    current_date = dt.now()
    formatted_date = current_date.strftime("%A, %B %d, %Y")
    openai_api_key = os.environ.get("OPENAI_API_KEY")
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
        + "My business hours are "
        + business_hours
        + " of my time zone. "
        + "I am not free outside these times so don't recomment times outside these business hours. "
    )

    # Add the email prompt if the user interacts via email
    if interface == "email":
        assistant_instructions = (
            assistant_instructions
            + "I will send you requests in an email that start with the phrase 'Hi Monica, '."
            + "Always respond to my requests either with the answer, or a description of the task you performed after you performed it."
            + "Respond always in HTML using only <br> tags for spacing between paragraphs. Do not use <p> tags for paragraph formatting, as they may not render correctly in email clients."
            + "Do not ever respond using markdown formatting, code block tags, or any other markup language."
            + "The following is a valid response example: 'Hi [Recipient],<br><br>This is the first line or paragraph.<br>"
            + "These are time slots in one day shown in bullet form:<ul><li>8:00 am - 9:00 am EST</li>"
            + "<li>11:00 am - 1:00 pm EST</li><li>3:00 pm - 4:00 pm EST</li></ul><br>"
            + "This is the second paragraph with an <i>italicized</i> word. Below are time slots across multiple days.<ul>"
            + "<li>Thursday, Oct. 3"
            + "<ul><li>8:00 am - 9:00 am GMT</li><li>11:00 am - 1:00 pm GMT</li><li>3:00 pm - 4:00 pm EST</li>"
            + "</ul></li><li>Friday, Oct. 4<ul><li>8:00 am - 9:00 am GMT</li><li>11:00 am - 1:00 pm GMT</li>"
            + "<li>3:00 pm - 4:00 pm GMT</li></ul></li></ul><br>This is the last line or paragraph with a <b>bolded</b> word for emphasis."
            + "<br><br><br>Best,<br><br>Monica A. Ingenio<br><i>(OpenAI-Powered Assistant in Beta, please excuse any "
            + "mistakes)</i><br><br>"
        )

    # Add the debug prompt if user runs with debug
    if debug:
        assistant_instructions = (
            assistant_instructions
            + "Please remember to track and document all interactions using the following format.\n "
            + "Start of Interaction: Briefly note the request. Follow these steps:\n"
            + "Prompt: Briefly describe the user request.\nTool Call: List the function used and key parameters.\n"
            + "Result: Summarize the result or action taken.\n"
            + "Repeat as needed for each step in the interaction. Conclude with any noteworthy observations.\n"
            + "End of Interaction\nIf I request a compilation of these interactions, ensure you're able to share"
            + " the documented interaction logs accurately and comprehensively, adhering to the detailed format I shared with you."
        )

    # Add the toolkit prompt
    assistant_instructions = assistant_instructions + toolkit_prompt

    client = OpenAI(
        api_key=openai_api_key,
    )

    assistant = client.beta.assistants.create(
        name="AI Administrative Assistant",
        instructions=assistant_instructions,
        model=model,
        tools=tools,
        temperature=0.05
    )

    thread = client.beta.threads.create()

    return client, assistant, thread


def run_prompt(prompt, client, assistant, thread):
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=prompt,
    )

    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
    )
    return run


def poll_for_response(client, thread, run, model, debug=False, interface="cli"):
    LOOP_DELAY_SECONDS = 3

    while True:
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
        status = run.status

        if status == "completed":
            response = client.beta.threads.messages.list(thread_id=thread.id)
            if response.data:
                return response.data[0].content[0].text.value
            break
        elif status == "requires_action":
            tools_outputs = []

            for tool_call in run.required_action.submit_tool_outputs.tool_calls:
                tool_call_id = tool_call.id
                function_name = tool_call.function.name
                function_arguments = tool_call.function.arguments
                function_arguments = json.loads(function_arguments)

                # Case statement to execute each toolkit function
                if function_name == "o365search_emails":
                    output = o365search_emails(
                        **function_arguments, interface=interface
                    )
                elif function_name == "o365search_email":
                    output = o365search_email(**function_arguments, interface=interface)
                elif function_name == "o365search_events":
                    output = o365search_events(
                        **function_arguments, interface=interface
                    )
                elif function_name == "o365send_message":
                    output = o365send_message(**function_arguments, interface=interface)
                elif function_name == "o365send_event":
                    output = o365send_event(**function_arguments, interface=interface)
                elif function_name == "o365reply_message":
                    output = o365reply_message(
                        **function_arguments, interface=interface
                    )
                elif function_name == "o365find_free_time_slots":
                    output = o365find_free_time_slots(**function_arguments, interface=interface)

                # Clean the function output into JSON-like output
                output = pprint.pformat(output)
                tool_output = {"tool_call_id": tool_call_id, "output": output}
                tools_outputs.append(tool_output)

            if run.required_action.type == "submit_tool_outputs":
                client.beta.threads.runs.submit_tool_outputs(
                    thread_id=thread.id, run_id=run.id, tool_outputs=tools_outputs
                )

        elif status == "failed":
            return "Run failed try again!"
            break

        if debug:
            print("The Assistant's Status is: " + status)

        time.sleep(LOOP_DELAY_SECONDS)
