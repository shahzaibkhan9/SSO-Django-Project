# Generated by Django 4.2.4 on 2023-09-04 07:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0005_alter_app_email_verification_token'),
    ]

    operations = [
        migrations.AlterField(
            model_name='app',
            name='email_verification_token',
            field=models.CharField(blank=True, default=0, max_length=200),
            preserve_default=False,
        ),
    ]
