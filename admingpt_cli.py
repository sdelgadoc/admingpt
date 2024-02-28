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
coaching_loop = True
debug = False
model = "gpt-4-turbo-preview"
LOOP_DELAY_SECONDS = 3

# Main loop for the application
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

    (client, assistant, thread) = create_client(debug, model)
    run = run_prompt(prompt, client, assistant, thread)
    response = poll_for_response(client, thread, run, model, debug)
    print(response)

    time.sleep(LOOP_DELAY_SECONDS)
