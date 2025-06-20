from apps.TOPICS import TOPICS
from apps.producer import producer
from django.shortcuts import redirect, get_object_or_404
from rest_framework import status
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from django.conf import settings
from datetime import datetime
from django.conf import settings
from rest_framework.views import APIView
from django.db.models import Q
from django.core.cache import cache
from .customerserializer import CustomerSerializer
from .models import Customer
from apps.google_service import get_user_data
from apps.tasks import send_events
import jwt
from apps.validators import *
from apps.generate_token import generate_token
from urllib.parse import unquote
from apps.custom_authentication import UserAuthentication
from apps.custom_permission import IsUserAuthenticated

@api_view(["POST"])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([AllowAny])
def register(request):
    try:
        RegisterSchema(**request.data)
    except Exception as e:
        return Response(status=status.HTTP_422_UNPROCESSABLE_ENTITY, data={"error": str(e)})   
    try:
        Customer.objects.get(email=request.data.get("email"))
        return Response(status=status.HTTP_409_CONFLICT, data={"error": "a user with this email already exist"})
    except Customer.DoesNotExist:
        inviter = None
        if request.query_params:
            if len(request.query_params.keys()) == 1 and "invite_code" in request.query_params:
                invite_code = request.query_params.get("invite_code")
                inviter = get_object_or_404(Customer, invite_code=invite_code)
            else:
                return Response(statue=status.HTTP_400_BAD_REQUEST, data={"error": "invalid invite link"}) 
        serializer = CustomerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user = Customer.objects.get(email=request.data.get("email"))
        if inviter:
            user.assign_inviter(inviter=inviter)
        refresh = RefreshToken.for_user(user=user)
        token = generate_token()
        cache.set(token, str(refresh.access_token))
        redirect_url = f"http://localhost:5173/verify-email?token={token}"
        try:
            send_events(
                event="email_verification",
                topic="email_event",
                data={
                    "email": request.data.get("email"),
                    "verification_link": redirect_url,
                }
            )
        except Exception as e:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={"error": "Failed to send verification email"})
        return Response(status=status.HTTP_201_CREATED, data=serializer.data)
        


@api_view(["POST"])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([AllowAny])
def verify_email(request):
    try:
        VerifyEmailSchema(**request.data)
    except Exception as e:
        return Response(status=status.HTTP_422_UNPROCESSABLE_ENTITY, data={"error": str(e)})
    access_token = cache.get(request.data.get("token"), None)
    if access_token:
        try:
            user = jwt.decode(access_token, settings.SECRET_KEY, algorithms=["HS256"])
            customer = get_object_or_404(Customer, id=user.get("user_id"))
            cache.delete(request.data.get("token"))
            if customer.is_email_verified:
                return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": "Email already verified"})
            customer.verify_email()        
            return Response(status=status.HTTP_200_OK, data={"message": "email verified successfully"})
        except jwt.ExpiredSignatureError:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": "link expired"})
    return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": "Invalid token provided"})
    
@api_view(["POST"])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([AllowAny])
def login(request):
    try:
        LoginSchema(**request.data)
    except Exception as e:
        return Response(status=status.HTTP_422_UNPROCESSABLE_ENTITY, data={"error": str(e)})
    customer = get_object_or_404(Customer, email=request.data.get("email"))
    if not customer.check_password(request.data.get("password")):
        return Response(status=status.HTTP_401_UNAUTHORIZED, data={"error": "Invalid credentials"})
    if not customer.is_email_verified:
        refresh = RefreshToken.for_user(user=customer)
        token = generate_token()
        cache.set(token, str(refresh.access_token))
        redirect_url = f"http://localhost:5173/verify-email?token={token}"
        data = {
            "email": request.data.get("email"),
            "verification_link": redirect_url
        }
        try:
            send_events(
                event = "email_verification",
                topic = "email_event",
                data=data
            )
        except Exception as e:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={"error": "Failed to send verification email"})
        return Response(status=status.HTTP_403_FORBIDDEN, data={"error": "Email not verified"})
    refresh = RefreshToken.for_user(user=customer)
    response = Response(status=status.HTTP_200_OK, data={"id": customer.id, "email": customer.email})
    response.set_cookie(key="access_token", value=str(refresh.access_token), max_age=60 * 60 * 24, secure=False, httponly=True, samesite="Lax")
    response.set_cookie(key="refresh_token", value=str(refresh), max_age=60 * 60 * 24, secure=False, httponly=True, samesite="Lax")
    return response

@api_view(["POST"])
@authentication_classes([SessionAuthentication, BasicAuthentication])
def email(request):
    try:
        EmailSchema(**request.data)
    except Exception as e:
        return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": str(e)})
    customer = get_object_or_404(Customer, email=request.data.get("email"))
    token = generate_token()
    cache.set(key=token, value=customer.email, timeout=60 * 7)
    try:
        send_events(
            event = "password_reset",
            topic = "email_event",
            data={
                "email": request.data.get("email"),
                "redirect_url": f"http://127.0.0.1:5173/user/reset-password?token={token}"
            } 
        )
    except Exception as e:
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={"error": "Failed to send verification email"})
    return Response(status=status.HTTP_200_OK, data={"message": "verification link sent successfully"})

@api_view(["POST"])
@authentication_classes([SessionAuthentication, BasicAuthentication])
def password_reset(request):
    email = cache.get(request.query_params.get("token"), None)
    if email:
        try:
            PasswordResetSchema(**request.data)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": str(e)})
        customer = Customer.objects.get(email=email)
        if not customer.is_email_verified:
            customer.verify_email()
        customer.set_password(request.data.get("password"))
        customer.save()
        cache.delete(request.query_params.get("token"))
        return Response(status=status.HTTP_200_OK, data={"message": "password changed successfully"})
    else:
        return Response(status=status.HTTP_422_UNPROCESSABLE_ENTITY, data={"error": "invalid link provided"})


@api_view(['GET'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([AllowAny])
def google_auth(request):
    QUERY = {}
    for key, val in request.query_params.items():
        QUERY[key] = val
    try:
        print(QUERY)
        GoogleAuthSchema(**QUERY)
    except Exception as e:
        return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": str(e)})
    state = unquote(request.query_params.get("state"))
    data = {"code": request.query_params.get("code", None), "error": request.query_params.get("error", None)}
    redirect_url = settings.BASE_APP_URL + state
    try:
        user = get_user_data(validated_data=data)
    except Exception as e:
        return redirect(f'{redirect_url}?error={str(e)}')
    refresh = RefreshToken.for_user(user=user)
    message = "Login successful"
    if redirect_url:
        response = redirect(f'{redirect_url}?message={message}')
    else:
        response = redirect(f'{settings.BASE_APP_URL}?message={message}')
    response.set_cookie(key="access_token", value=str(refresh.access_token), max_age=60 * 60 * 24)
    response.set_cookie(key="refresh_token", value=str(refresh), max_age=60 * 60 * 24)
    return response


@api_view(["GET"])
@authentication_classes([SessionAuthentication, BasicAuthentication, UserAuthentication])
@permission_classes([IsUserAuthenticated])
def user_profile(request):
    data = {
        "id": request.user.id,
        "email": request.user.email
    }
    response = Response(status=status.HTTP_200_OK, data=data)
    if hasattr(request, "access_token"):
        response.set_cookie(key="access_token", value=str(request.access_token), max_age=60 * 60 * 24, secure=False, httponly=True, samesite="Lax")
    return response



@api_view(["GET"])
@authentication_classes([SessionAuthentication, BasicAuthentication, UserAuthentication])
@permission_classes([IsUserAuthenticated])
def logout(request):
    refresh_token = request.COOKIES.get('refresh_token')
    if not refresh_token:
        return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": "No refresh token provided in cookie"})
    token = RefreshToken(refresh_token)
    token.blacklist()
    response = Response(status=status.HTTP_200_OK, data={"message": "Logged out successfully"})
    response.cookies.clear()
    return response

@api_view(["GET"])
@authentication_classes([SessionAuthentication, BasicAuthentication, UserAuthentication])
@permission_classes([IsUserAuthenticated])
def invite_link(request):
    user = request.user
    if user.invite_code:
        return Response(status=status.HTTP_200_OK, data={"invite_link": f"http://127.0.0.1:5173/user/register?invite_code={user.invite_code}"})
    code = user.gen_invite_code()
    return Response(status=status.HTTP_200_OK, data={"invite_link": f"http://127.0.0.1:5173/user/register?invite_code={code}"})




