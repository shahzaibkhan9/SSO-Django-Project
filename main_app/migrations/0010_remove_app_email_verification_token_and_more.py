# Generated by Django 4.2.4 on 2023-09-06 07:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0009_app_app_url'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='app',
            name='email_verification_token',
        ),
        migrations.RemoveField(
            model_name='app',
            name='is_email_verified',
        ),
    ]
