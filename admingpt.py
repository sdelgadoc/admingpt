from openai import OpenAI
import time, json, pprint, os
from tools.o365_toolkit import (
    o365search_emails,
    o365search_email,
    o365search_events,
    o365parse_proposed_times,
    o365send_message,
    o365reply_message,
    o365send_event,
    tools,
)
from datetime import datetime as dt


# The main function to run the assistan
def run(email_platform: str = "outlook", debug: bool = False):
    # TO-DO: Add logic to support multiple mail platforms

    # Set values for global variables
    LOOP_DELAY_SECONDS = 2
    assistant_name = "Monica A. Ingenio"
    model = "gpt-4-1106-preview"
    current_date = dt.now()
    formatted_date = current_date.strftime("%A, %B %d, %Y")
    client_name = os.environ.get("CLIENT_NAME")
    client_email = os.environ.get("CLIENT_EMAIL")
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    assistant_instructions = (
        "You are an AI Administrative Assistant called "
        + assistant_name
        + ", and I am your executive. My name is "
        + client_name
        + ". My email is: "
        + client_email
        + ", in the Eastern Time (ET)."
        " You have access to my email and calendar. Today is "
        + formatted_date
        + ". "
    )

    # Add the debug prompt if user runs with debug
    if debug:
        debug_prompt = (
            "Keep a record of any feedback requests provided by me"
            " detailing the prompt and tools calls in case I want to retrieve"
            " them."
        )
    else:
        debug_prompt = ""
    assistant_instructions = assistant_instructions + debug_prompt

    client = OpenAI(
        api_key=openai_api_key,
    )

    assistant = client.beta.assistants.create(
        name="AI Administrative Assistant",
        instructions=assistant_instructions,
        model=model,
        tools=tools,
    )

    ### The following prompt can be used to debug an interaction:
    ### Using the same format I used earlier in this interaction, please provide a record of any feedback requests provided by me in this interaction detailing the prompt and tools calls so I can reference them in the future.

    thread = client.beta.threads.create()
    my_thread_id = thread.id
    # Used to run coaching process in the first iteration
    coaching_loop = True

    while True:
        # If it's the first loop, coach the Assistant, otherwise request prompt
        if coaching_loop:
            coaching_loop = False
            # Open the file and read its contents
            with open("coaching_data.txt", "r") as file:
                prompt = file = file.read()
        else:
            prompt = input("Enter your request here: ")
            if prompt.lower() == "stop":
                break

        # Create a message
        message = client.beta.threads.messages.create(
            thread_id=my_thread_id,
            role="user",
            content=prompt,
        )

        # Run
        run = client.beta.threads.runs.create(
            thread_id=my_thread_id,
            assistant_id=assistant.id,
        )
        my_run_id = run.id

        while True:
            run = client.beta.threads.runs.retrieve(
                thread_id=my_thread_id, run_id=my_run_id
            )
            status = run.status

            if status == "completed":
                response = client.beta.threads.messages.list(thread_id=my_thread_id)
                if response.data:
                    print(response.data[0].content[0].text.value)
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
                        output = o365search_emails(**function_arguments)
                    elif function_name == "o365search_email":
                        output = o365search_email(**function_arguments)
                    elif function_name == "o365search_events":
                        output = o365search_events(**function_arguments)
                    elif function_name == "o365parse_proposed_times":
                        output = o365parse_proposed_times(
                            **function_arguments, client=client, model=model
                        )
                    elif function_name == "o365send_message":
                        output = o365send_message(**function_arguments)
                    elif function_name == "o365send_event":
                        output = o365send_event(**function_arguments)
                    elif function_name == "o365reply_message":
                        output = o365reply_message(**function_arguments)

                    # Clean the function output into JSON-like output
                    output = pprint.pformat(output)
                    tool_output = {"tool_call_id": tool_call_id, "output": output}
                    tools_outputs.append(tool_output)

                if run.required_action.type == "submit_tool_outputs":
                    client.beta.threads.runs.submit_tool_outputs(
                        thread_id=thread.id, run_id=run.id, tool_outputs=tools_outputs
                    )

            elif status == "failed":
                print("Run failed try again!")
                break

            time.sleep(LOOP_DELAY_SECONDS)

        time.sleep(LOOP_DELAY_SECONDS)


if __name__ == "__main__":
    run(email_platform="outlook", debug=True)
