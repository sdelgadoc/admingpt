import os, time
from globals import token, st


def clean_body(body: str) -> str:
    """Clean body of a message or event."""
    try:
        from bs4 import BeautifulSoup

        try:
            # Remove HTML
            soup = BeautifulSoup(str(body), "html.parser")
            body = soup.get_text()

            # Remove return characters
            body = "".join(body.splitlines())

            # Remove extra spaces
            body = " ".join(body.split())

            return str(body)
        except Exception:
            return str(body)
    except ImportError:
        return str(body)


def authenticate_token():
    global token

    # Assign the token value from the session state
    token = st.session_state.token


def streamlit_consent_input_token(consent_url):
    global st

    response = "Click on the [following link to authenticate]("
    response = response + consent_url
    response = (
        response
        + ") with the Microsoft Graph API. Then, copy and paste the URL you are"
        " forwarded to in the text box immediately below."
    )

    st.write(response)
    message = {"role": "assistant", "content": response}
    st.session_state.messages.append(message)

    st.text_input("Input token", key="token", on_change=authenticate_token)

    # This is kludgy solution to waiting until the user enters token into the textbox
    while token == None:
        time.sleep(2)

    return token


def authenticate(streamlit=False):
    """Authenticate using the Microsoft Grah API"""
    try:
        from O365 import Account
    except ImportError as e:
        raise ImportError(
            "Cannot import 0365. Please install the package with `pip install O365`."
        ) from e

    if "CLIENT_ID" in os.environ and "CLIENT_SECRET" in os.environ:
        client_id = os.environ["CLIENT_ID"]
        client_secret = os.environ["CLIENT_SECRET"]
        credentials = (client_id, client_secret)
    else:
        print(
            "Error: The CLIENT_ID and CLIENT_SECRET environmental variables have not "
            "been set. Visit the following link on how to acquire these authorization "
            "tokens: https://learn.microsoft.com/en-us/graph/auth/"
        )
        return None

    account = Account(credentials)

    if account.is_authenticated is False:
        if streamlit == False:
            if not account.authenticate(
                scopes=[
                    "https://graph.microsoft.com/Mail.ReadWrite",
                    "https://graph.microsoft.com/Mail.Send",
                    "https://graph.microsoft.com/Calendars.ReadWrite",
                    "https://graph.microsoft.com/MailboxSettings.ReadWrite",
                    "https://graph.microsoft.com/User.Read",
                    "https://graph.microsoft.com/User.ReadBasic.All",
                ],
            ):
                print("Error: Could not authenticate")
                return None
            else:
                return account
        else:
            if not account.authenticate(
                scopes=[
                    "https://graph.microsoft.com/Mail.ReadWrite",
                    "https://graph.microsoft.com/Mail.Send",
                    "https://graph.microsoft.com/Calendars.ReadWrite",
                    "https://graph.microsoft.com/MailboxSettings.ReadWrite",
                    "https://graph.microsoft.com/User.Read",
                    "https://graph.microsoft.com/User.ReadBasic.All",
                ],
                handle_consent=streamlit_consent_input_token,
            ):
                print("Error: Could not authenticate")
                return None
            else:
                return account
    else:
        return account


"""UTC format for datetime objects."""
UTC_FORMAT = "%Y-%m-%dT%H:%M:%S%z"
