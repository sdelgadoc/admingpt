# email_service/urls.py

from django.urls import path
from .views import ProcessEmailView

urlpatterns = [
    path("process-email/", ProcessEmailView.as_view(), name="process_email"),
]
