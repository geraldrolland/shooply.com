from rest_framework.serializers import ModelSerializer, CharField
from .models import *

class CustomerSerializer(ModelSerializer):
    password = CharField(write_only=True)
    
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