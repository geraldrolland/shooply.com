from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from datetime import timezone, datetime
from .customusermanager import CustomerManager
import uuid
from random import choice

class Customer(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_("email address"), unique=True, db_index=True)
    is_email_verified = models.BooleanField(null=False, default=False)
    has_min_purchase = models.BooleanField(null=False, default=False)
    invite_code = models.CharField(null=True, max_length=1084, db_index=True)
    inviter = models.ForeignKey("self", on_delete=models.CASCADE, related_name="invitee", null=True)
    type = models.CharField(max_length=24, default="customer", editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    objects = CustomerManager()

    def __str__(self):
        return self.email
    
    def gen_invite_code(self):
        code = ""
        for i in range(0, 11):
            code += choice(['0', '1', '2', '3',
                            '4', '5', '6', '7',
                            '8', '9'
                            ])
        self.invite_code = code
        self.updated_at = datetime.now(timezone.utc)
        self.save()
        return code
    
    def verify_email(self):
        self.is_email_verified = True
        self.updated_at = datetime.now(timezone.utc)
        self.save()

    def assign_inviter(self, inviter):
        self.inviter = inviter
        self.save()

