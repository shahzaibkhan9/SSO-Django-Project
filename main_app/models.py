from django.contrib.auth.models import User
from django.db import models


class App(models.Model):
    name = models.CharField(max_length=100)
    app_url = models.URLField(max_length=100, default="")
    icon = models.ImageField(upload_to="static/app_icons/")

    class Meta:
        app_label = "main_app"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    allowed_apps = models.ManyToManyField(App)

    class Meta:
        app_label = "main_app"


class EmailVerification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"EmailVerification for {self.user.username}"
