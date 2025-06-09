from apps.TOPICS import TOPICS
from apps.encrypt_data import encrypt_data
from apps.producer import producer
from django.shortcuts import redirect, get_object_or_404
from rest_framework import viewsets, status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_ratelimit.decorators import ratelimit
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.views.decorators.vary import vary_on_cookie
from django.utils.decorators import method_decorator
from rest_framework.decorators import api_view, permission_classes, authentication_classes, parser_classes
import random
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
import requests
import base64
import uuid
import json
from datetime import datetime
from django.conf import settings
from rest_framework.views import APIView
from django.db.models import Q
from django.core.cache import cache
from .customerserializer import CustomerSerializer
from .models import Customer
from .pswd_validation_str import pswd_validation_str
import re
from apps.tasks import send_events
import jwt
from email_validator import validate_email, EmailNotValidError



@api_view(["POST"])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([AllowAny])
def register(request):
    try:
        Customer.objects.get(email=request.data.get("email"))
        return Response(status=status.HTTP_409_CONFLICT, data={"error": "a user with this email already exist"})
    except Customer.DoesNotExist:
        try:
            validate_email(request.data.get("email"))
        except EmailNotValidError as e:
            return Response(status=status.HTTP_422_UNPROCESSABLE_ENTITY, data={"error": str(e)})
        if not re.fullmatch(pswd_validation_str, request.data.get("password")):
            error_msg = "Passwords must be a minimum of 8 characters long, contain at least one uppercase letter, one number, and one special character."
            return Response(status=status.HTTP_422_UNPROCESSABLE_ENTITY, data={"error": error_msg})
        elif request.data.get("confirm_password") is None or request.data.get("confirm_password").strip() == "":
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": "confirm password is required"})
        elif request.data.get("confirm_password") != request.data.get("password"):
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": "password do not match"})
        else:
            serializer = CustomerSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            user = Customer.objects.get(email=request.data.get("email"))
            refresh = RefreshToken.for_user(user=user)
            redirect_url = f"http://localhost:5173/verify-email?token={refresh.access_token}"
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
    token = request.data.get("token")
    if not token:
        return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": "Token is required"})
    try:
        user = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        customer = get_object_or_404(Customer, id=user.get("user_id"))
        if customer.is_email_verified:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": "Email already verified"})
        customer.verify_email()
        refresh = RefreshToken.for_user(user=customer)
        response = Response(status=status.HTTP_200_OK, data={"access": str(refresh.access_token)})
        response.set_cookie(
            key='access_token',
            value=str(refresh.access_token),
            httponly=True,
            secure=False,
            samesite='Lax',
            max_age=60 * 60 * 24 * 3  
        )
        response.set_cookie(
            key="refresh_token",
            value=str(refresh),
            httponly=True,
            secure=False,
            samesite='Lax',
            max_age=60 * 60 * 24 * 3 
        )
        return response
    except jwt.ExpiredSignatureError:
        return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": "link expired"})
    except jwt.InvalidTokenError:
        return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": "Invalid token"})