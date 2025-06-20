from django.urls import path
from .views import register, verify_email, login, email, password_reset, google_auth, user_profile, logout, invite_link


urlpatterns = [
    path('register', register),
    path('verify-email', verify_email),
    path('log-in', login),
    path('email', email),
    path('password-reset', password_reset),
    path('google-auth/', google_auth),
    path('profile', user_profile),
    path('log-out', logout),
    path("invite-link", invite_link)
    
]