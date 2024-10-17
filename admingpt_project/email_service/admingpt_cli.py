import os, time
from utils import create_client, run_prompt, poll_for_response

## Assign environmental files
# Set your OpenAI API key
os.environ["OPENAI_API_KEY"] = "YOUR OPENAI KEY"
# Set your Microsoft Graph client ID
os.environ["CLIENT_ID"] = "YOUR CLIENT ID"
# Set your Microsoft Graph client secret
os.environ["CLIENT_SECRET"] = "YOUR CLIENT SECRET"

# Assign constants
first_loop = True
debug = False
model = "gpt-4o-2024-08-06"
LOOP_DELAY_SECONDS = 3

# Main loop for the application
while True:

    if first_loop:
        # Start with a default prompt
        prompt = 'Confirm you\'re ready by replying, "Hello, [MY FULL NAME]. How can I assist you today?"'
        first_loop = False
    else:
        prompt = input("Enter your request here: ")
        if prompt.lower() == "stop":
            break

    (client, assistant, thread) = create_client(debug, model)
    run = run_prompt(prompt, client, assistant, thread)
    response = poll_for_response(client, thread, run, model, debug)
    print(response)

    time.sleep(LOOP_DELAY_SECONDS)
