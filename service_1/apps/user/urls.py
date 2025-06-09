from django.urls import path
from .views import register, verify_email
urlpatterns = [
    path('register', register),
    path('verify-email', verify_email),
]