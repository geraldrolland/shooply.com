from kafka import KafkaProducer
import json
from django.conf import settings
from apps.encrypt_data import encrypt_data

producer = KafkaProducer(
    bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
    #value_serializer=lambda v: json.dumps(v).encode('utf-8'),
)

