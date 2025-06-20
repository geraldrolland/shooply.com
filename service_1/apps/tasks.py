from .producer import producer
from .encrypt_data import encrypt_data
from django.core.mail import EmailMessage
from celery import shared_task
import logging
import json

@shared_task(queue='high_priority', priority=0)  # Priority 0 is highest
def send_events(event, topic,  data):
    logger = logging.getLogger(__name__)
    logger.info("Task started: send_events")
    payload = {
        "event": event,
        "data": data,
        }
    data = encrypt_data(payload)
    #data = payload
    #producer.send(topic=topic, value=json.dumps(data).encode('utf-8'))
    producer.send(topic=topic, value=data.encode('utf-8'))
    producer.flush()