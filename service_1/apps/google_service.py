from django.conf import settings
from django.shortcuts import redirect
from django.core.exceptions import ValidationError
from urllib.parse import urlencode
from typing import Dict, Any
import requests
from .user.models import *

# Constants for Google OAuth URLs
GOOGLE_ACCESS_TOKEN_OBTAIN_URL = 'https://oauth2.googleapis.com/token'
GOOGLE_USER_INFO_URL = 'https://www.googleapis.com/oauth2/v3/userinfo'
LOGIN_URL = f'{settings.BASE_APP_URL}/log-in'

# Exchange authorization token with access token
def google_get_access_token(code: str, redirect_uri: str) -> str:
    data = {
        'code': code,
        'client_id': settings.GOOGLE_CLIENT_ID,
        'client_secret': settings.GOOGLE_CLIENT_SECRET,
        #'redirect_uri': 'http://127.0.0.1:8000/api/user/google-auth/',
        'redirect_uri': redirect_uri,
        'grant_type': 'authorization_code'
    }
    response = requests.post(GOOGLE_ACCESS_TOKEN_OBTAIN_URL, data=data)
    if not response.ok:
        raise ValidationError('Could not get access token from Google.')
    access_token = response.json()['access_token']
    return access_token

# Get user info from google
def google_get_user_info(access_token: str) -> Dict[str, Any]:
    response = requests.get(
        GOOGLE_USER_INFO_URL,
        params={'access_token': access_token}
    )

    if not response.ok:
        raise ValidationError('Could not get user info from Google.')
    return response.json()


def get_user_data(validated_data):
    domain = settings.BASE_API_URL
    redirect_uri = f'{domain}/api/user/google-auth/'
    code = validated_data.get('code')
    error = validated_data.get('error')
    if error or not code:
        raise ValidationError("access denied")
    
    access_token = google_get_access_token(code=code, redirect_uri=redirect_uri)
    user_data = google_get_user_info(access_token=access_token)

    # Creates user in DB if first time login
    try:
        user = Customer.objects.get(email=user_data['email'])
        if not user.is_email_verified:
            user.verify_email()
    except Customer.DoesNotExist:
        user = Customer.objects.get_or_create(
        email=user_data['email'],
    )
        user.set_password(user_data.get("password"))
        user.save()
        user = Customer.objects.get(email=user_data['email'])
        user.verify_email()
    return user