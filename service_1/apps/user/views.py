
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
@api_view(["POST"])
def register(request):
    print(request.data.get("email"))
    try:
        Customer.objects.get(email=request.data.get("email"))
        return Response(status=status.HTTP_409_CONFLICT, data={"error": "a user with this email already exist"})
    except Customer.DoesNotExist:
        if not re.fullmatch(pswd_validation_str, request.data.get("password")):
            error_msg = "Passwords must be a minimum of 8 characters long, contain at least one uppercase letter, one number, and one special character."
            return Response(status=status.HTTP_422_UNPROCESSABLE_ENTITY, data={"error": error_msg})
        elif request.data.get("confirm_password") != request.data.get("password"):
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": "password do not match"})
        else:
            user = CustomerSerializer(data=request.data)
            user.is_valid(raise_exception=True)
            user.save()
            return Response(status=status.HTTP_201_CREATED, data=user.data)
