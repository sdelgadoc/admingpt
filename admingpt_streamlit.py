import os
from tools.utils import authenticate

# Importing streamlit from global file to help with authentication
from globals import st
from utils import create_client, run_prompt, poll_for_response

st.set_page_config(page_title="AdminGPT - Beta 🤖📋 ")

st.title("AdminGPT - Beta 🤖📋")


# Callback to setup authentication credentials
def setup_credentials():
    if (
        st.session_state.openai_key != ""
        and st.session_state.client_id != ""
        and st.session_state.client_secret != ""
    ):
        # Save authentication tokens to environmental variables
        os.environ["OPENAI_API_KEY"] = st.session_state.openai_key
        os.environ["CLIENT_ID"] = st.session_state.client_id
        os.environ["CLIENT_SECRET"] = st.session_state.client_secret

        # Run the authentication function
        account = authenticate(True)
        print(account)


# Create the sidebar and all of its text boxes
with st.sidebar:
    st.title("AdminGPT - Beta 🤖📋 ")
    openai_api_key = st.text_input(
        "OpenAI API Key", type="password", key="openai_key", on_change=setup_credentials
    )
    client_id = st.text_input(
        "Microsoft Graph Client ID",
        type="password",
        key="client_id",
        on_change=setup_credentials,
    )
    client_secret = st.text_input(
        "Microsoft Graph Client Secret",
        type="password",
        key="client_secret",
        on_change=setup_credentials,
    )
    debug = st.toggle("Debug model?")
    if not (openai_api_key and client_id and client_secret):
        st.warning("Please enter your credentials!", icon="⚠️")
    else:
        st.success("Proceed to entering your prompt message!", icon="👉")
    st.markdown(
        "📖 Learn how to build this app in [Github"
        " repo](https://github.com/sdelgadoc/AdminGPT)!"
    )


st.write(
    "Your AI-Powered Administrative Assistant, powered by OpenAI's Assistant Framework"
)

if "messages" not in st.session_state.keys():
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! Welcome to the AdminGPT Beta."}
    ]

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# User-provided prompt
if prompt := st.chat_input(
    disabled=not (openai_api_key and client_id and client_secret)
):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

# Instantiate variables before generating content
client = None
assistant = None
thread = None
model = "gpt-4-1106-preview"
# Generate a new response if last message is not from assistant
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            # If you haven't already, create a client and load coaching data
            if (
                "client" not in st.session_state.keys()
                and "assistan" not in st.session_state.keys()
                and "thread" not in st.session_state.keys()
            ):
                (
                    st.session_state.client,
                    st.session_state.assistant,
                    st.session_state.thread,
                ) = create_client(debug, model)
                with open("coaching_data.txt", "r") as file:
                    coaching_prompt = file.read()

                run = run_prompt(
                    coaching_prompt,
                    st.session_state.client,
                    st.session_state.assistant,
                    st.session_state.thread,
                )

                response = poll_for_response(
                    st.session_state.client, st.session_state.thread, run, model, debug
                )

            run = run_prompt(
                prompt,
                st.session_state.client,
                st.session_state.assistant,
                st.session_state.thread,
            )
            response = poll_for_response(
                st.session_state.client, st.session_state.thread, run, model, debug
            )
            st.write(response)

    message = {"role": "assistant", "content": response}
    st.session_state.messages.append(message)

### APPENDIX: The following prompt can be used to debug an interaction:
### Using the same format I used earlier in this interaction, please provide a record of any feedback requests provided by me in this interaction detailing the prompt and tools calls so I can reference them in the future.
