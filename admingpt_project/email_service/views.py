# email_service/views.py

import os
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.views import View
from .models import ProcessedEmail, TokenModel, AuthenticationState
from django.conf import settings
from .utils import (
    create_client,
    run_prompt,
    poll_for_response,
    assistant_first_name,
)
from .tools.utils import authenticate
from datetime import datetime as dt
from openai import OpenAI
from .tools.o365_toolkit import (
    o365search_emails,
    o365search_email,
    o365reply_message,
)
from O365 import Account
from O365.utils import DjangoTokenBackend

class ProcessEmailView(View):
    assistant_first_name = "Monica"

    def get(self, request):
        try:
            # Assign constants
            model = "gpt-4o"

            # Get prompt email
            prompt, message_id, call = self.get_prompt_email()

            # Check if the email has already been processed
            if ProcessedEmail.objects.filter(message_id=message_id).exists():
                return JsonResponse(
                    {
                        "status": "skipped",
                        "message": "Email has already been processed.",
                    }
                )

            # Check if the email prompt starts with "Hi {assistant_first_name}"
            if not call:
                # Save the processed message_id to the database
                ProcessedEmail.objects.create(message_id=message_id)

                return JsonResponse(
                    {
                        "status": "skipped",
                        "message": "Email includes call, but does not start with it.",
                    }
                )

            # Create client, assistant, and thread
            client, assistant, thread = create_client(
                debug=False, model=model, interface="email"
            )

            # Run prompt
            run = run_prompt(prompt, client, assistant, thread)

            # Poll for response
            response = poll_for_response(client, thread, run, model)

            # Reply to the email
            reply = o365reply_message(
                message_id,
                response,
                interface="email",
                reply_to_sender=True,
            )

            # Save the processed message_id to the database
            ProcessedEmail.objects.create(message_id=message_id)

            return JsonResponse({"status": "success", "reply": reply})

        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

    def get_prompt_email(self):
        # Authenticate user
        account = authenticate(interface="email")
        directory = account.directory(resource="me")
        user = directory.get_current_user()
        client_email = user.mail

        query = (
            f"from:{client_email} to:{client_email} body:'Hi {assistant_first_name}, '"
        )

        emails = o365search_emails(query, "inbox", 5)

        if not emails:
            raise ValueError("No emails found matching the query.")

        # Sort emails based on date
        emails.sort(key=lambda x: x["date"], reverse=True)

        # Get the latest email
        message_id = emails[0]["message_id"]
        email = o365search_email(message_id)
        call = emails[0]["body"].startswith(f"Hi {assistant_first_name}, ")

        return str(email), message_id, call

class AuthenticationView(View):
    def get(self, request):
        # Step 1: Initiate OAuth process and redirect to Microsoft login
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

        account = Account(credentials)
        
        # Callback URL for OAuth step two
        callback = request.build_absolute_uri(reverse('authentication_callback'))
        
        # Get authorization URL and state
        url, state = account.con.get_authorization_url(
            requested_scopes=[
                "https://graph.microsoft.com/Mail.ReadWrite",
                "https://graph.microsoft.com/Mail.Send",
                "https://graph.microsoft.com/Calendars.ReadWrite",
                "https://graph.microsoft.com/MailboxSettings.ReadWrite",
                "https://graph.microsoft.com/User.Read",
                "https://graph.microsoft.com/User.ReadBasic.All",
                'offline_access'
            ],
            redirect_uri=callback
        )
        
        # Store the state in the database
        AuthenticationState.objects.create(state=state)
        
        # Redirect to Microsoft login
        return HttpResponseRedirect(url)

class AuthenticationCallbackView(View):
    def get(self, request):
        # Handle the callback from Microsoft login
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

        # Use the Django token backend to store the token
        token_backend = DjangoTokenBackend(token_model=TokenModel)
        account = Account(credentials, token_backend=token_backend)
        
        # Retrieve the saved state from the database
        saved_state = AuthenticationState.objects.latest('created_at')
        
        if not saved_state:
            return JsonResponse({"status": "error", "message": "Invalid state."}, status=400)
        
        # Build the callback URL
        callback = request.build_absolute_uri(reverse('authentication_callback'))
        
        # Requested URL includes the authentication information
        requested_url = request.build_absolute_uri()
        
        # Complete token request
        result = account.con.request_token(
            requested_url,
            state=saved_state.state,
            redirect_uri=callback
        )

        return HttpResponseRedirect("https://github.com/sdelgadoc/AdminGPT")
