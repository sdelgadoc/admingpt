import os, pprint, json, time
from datetime import datetime as dt
from openai import OpenAI
from tools.o365_toolkit import (
    o365search_emails,
    o365search_email,
    o365search_events,
    o365parse_proposed_times,
    o365send_message,
    o365reply_message,
    o365send_event,
    o365find_free_time_slots,
    tools,
    toolkit_prompt,
)
from tools.utils import authenticate


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
    assistant_name = "Monica A. Ingenio"
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
        + " timezone. You have access to my email and calendar. Today is "
        + formatted_date
        + ". ALWAYS use available functions to determine "
        + "whether I am available at a certain time in my caledar.\n"
        + toolkit_prompt
    )

    # Add the debug prompt if user runs with debug
    if debug:
        debug_prompt = (
            "Please remember to track and document all interactions using the following format.\n "
            + "Start of Interaction: Briefly note the request. Follow these steps:\n"
            + "Prompt: Briefly describe the user request.\nTool Call: List the function used and key parameters.\n"
            + "Result: Summarize the result or action taken.\n"
            + "Repeat as needed for each step in the interaction. Conclude with any noteworthy observations.\n"
            + "End of Interaction\nIf I request a compilation of these interactions, ensure you're able to share"
            + " the documented interaction logs accurately and comprehensively, adhering to the detailed format I shared with you."
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


def run_prompt(prompt, client, assistant, thread):
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=prompt,
    )

    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
        temperature=0.2,
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
                elif function_name == "o365parse_proposed_times":
                    output = o365parse_proposed_times(
                        **function_arguments, client=client, model=model
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
                    output = o365find_free_time_slots(**function_arguments)

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
