# Generated by Django 4.2.6 on 2025-06-06 05:48

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='has_min_purchase',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='customer',
            name='invite_code',
            field=models.CharField(db_index=True, max_length=1084, null=True),
        ),
        migrations.AddField(
            model_name='customer',
            name='inviter',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='invitee', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='customer',
            name='type',
            field=models.CharField(default='customer', editable=False, max_length=24),
        ),
    ]
