from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .user.models import Customer
import jwt
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings

class UserAuthentication(BaseAuthentication):
    def authenticate(self, request):
        print("THIS IS THE REQUEST", request)
        access_token = request._request.COOKIES.get('access_token')
        
        if not access_token:
            raise AuthenticationFailed('No access token provided')
        try:
            user = jwt.decode(
                access_token,
                key=settings.SECRET_KEY, 
                algorithms=["HS256"]  # Use the same algorithm as your JWT creation
            )
        except jwt.ExpiredSignatureError:
            refresh_token = request._request.COOKIES.get('refresh_token')
            if not refresh_token:
                raise AuthenticationFailed('Token has expired and no refresh token provided')
            
            try:
                # Decode the refresh token to get the user ID
                user = jwt.decode(
                    refresh_token,
                    key=settings.SECRET_KEY, 
                    algorithms=["HS256"]
                )
                access_token = RefreshToken(refresh_token).access_token
                request.access_token = str(access_token)  # Update the access token cookie
            except jwt.DecodeError:
                raise AuthenticationFailed('Invalid refresh token')
            except jwt.ExpiredSignatureError:
                raise AuthenticationFailed('Refresh token has expired')

        except jwt.DecodeError:
            raise AuthenticationFailed('Invalid token')
        try:
            user = Customer.objects.get(id=user['user_id'])
        except Customer.DoesNotExist:
            raise AuthenticationFailed('User not found')
        request.user = user
        return (user, None)  # Must return a tuple of (user, auth)
