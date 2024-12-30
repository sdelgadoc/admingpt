# email_service/urls.py

from django.urls import path
from .views import ProcessEmailView, AuthenticationView, AuthenticationCallbackView

urlpatterns = [
    path("process-email/", ProcessEmailView.as_view(), name="process_email"),
    path("authenticate/", AuthenticationView.as_view(), name='authentication'),
    path("authenticate_callback/", AuthenticationCallbackView.as_view(), name='authentication_callback'),
]
