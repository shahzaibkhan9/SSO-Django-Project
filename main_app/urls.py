from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("otp/", views.otp_view, name="otp"),
    path("logout/", views.logout_user, name="logout"),
    path("register/", views.register_user, name="register_user"),
    path("add_app/", views.add_app, name="add_app"),
    path("user_list/", views.user_list, name="user_list"),
    path("edit_user/<int:user_id>/", views.edit_user, name="edit_user"),
    path("verify_email/<str:token>/",
         views.verify_email_view, name="verify_email"),
]
