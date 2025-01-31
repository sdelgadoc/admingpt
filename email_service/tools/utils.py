import os

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


def authenticate(interface="cli"):
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

    if interface == "cli":
        account = Account(credentials)
    elif interface == "email":
        from ..models import TokenModel
        from O365.utils import DjangoTokenBackend
        
        # Use the Django token backend to store the token
        token_backend = DjangoTokenBackend(token_model=TokenModel)
        account = Account(credentials, token_backend=token_backend)

    if account.is_authenticated is False:
        if not account.authenticate(
            scopes=[
                "https://graph.microsoft.com/Mail.ReadWrite",
                "https://graph.microsoft.com/Mail.Send",
                "https://graph.microsoft.com/Calendars.ReadWrite",
                "https://graph.microsoft.com/MailboxSettings.ReadWrite",
                "https://graph.microsoft.com/User.Read",
                "https://graph.microsoft.com/User.ReadBasic.All",
                'offline_access'
            ],
        ):
            print("Error: Could not authenticate")
            return None
        else:
            return account

    else:
        return account


"""UTC format for datetime objects."""
UTC_FORMAT = "%Y-%m-%dT%H:%M:%S%z"
