from rest_framework.serializers import ModelSerializer, CharField, BooleanField
from .models import *

class CustomerSerializer(ModelSerializer):
    password = CharField(write_only=True)
    email = CharField(required=True, allow_blank=False)
    has_min_purchase = BooleanField(read_only=True, default=False)
    invite_code = CharField(read_only=True, default=None, write_only=False)
    type = CharField(read_only=True, default="customer")   
    class Meta:
        model = Customer
        fields = ['id', 'is_email_verified', 'has_min_purchase', 'invite_code', 'type', 'created_at', 'updated_at', 'password', 'email']

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = Customer.objects.create(**validated_data)
        user.set_password(password)
        return user
    
    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            if key == "password":
                instance.set_password(value)
                continue
            if value:
                setattr(instance, key, value)
        instance.updated_at = datetime.now()
        instance.save()
        return instance