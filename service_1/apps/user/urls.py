from django.urls import path
from .views import register, verify_email, login, email, password_reset
urlpatterns = [
    path('register', register),
    path('verify-email', verify_email),
    path('log-in', login),
    path('email', email),
    path('password-reset', password_reset),
]