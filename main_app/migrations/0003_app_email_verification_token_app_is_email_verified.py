# Generated by Django 4.2.4 on 2023-09-04 07:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0002_app_app_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='app',
            name='email_verification_token',
            field=models.CharField(default=None, max_length=200),
        ),
        migrations.AddField(
            model_name='app',
            name='is_email_verified',
            field=models.BooleanField(default=False),
        ),
    ]
