import re
import uuid

# from .utils import send_otp
from datetime import datetime, timedelta

import pyotp
from django.contrib import messages  # Import messages module
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import SignUpForm  # Import your SignUpForm
from .forms import AppCreationForm, UserAppAssignmentForm
from .models import App, EmailVerification, UserProfile


def home(request):
    if request.user.is_authenticated:
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            allowed_apps = user_profile.allowed_apps.all()
            app_count = App.objects.all().count()
            users = User.objects.all().count()

            user = request.user
            active_users = User.objects.filter(is_active=True).count()
            # active_users = user.is_active.all().count()
            return render(
                request,
                "main/dashboard/dashboard.html",
                {
                    "allowed_apps": allowed_apps,
                    "app_count": app_count,
                    "users": users,
                    "active_users": active_users,
                },
            )
        except UserProfile.DoesNotExist:
            # messages.warning(request, "You don't have an assigned profile. Contact an administrator.")
            # return render(request, 'main/dashboard/dashboard.html', {'allowed_apps': []})
            return render(request, "main/dashboard/dashboard.html", {})

    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(request, username=username, password=password)
        if user is not None:
            totp = pyotp.TOTP(pyotp.random_base32(), interval=240)

            # user entering otp to match with topt
            otp = totp.now()

            request.session["otp_secret_key"] = totp.secret

            # Entering valdity of code for 1 minute
            valid_date = datetime.now() + timedelta(minutes=3)

            request.session["otp_valid_Date"] = str(valid_date)

            # Printing on console

            print(f"Your one time password is {otp}")

            current_site = get_current_site(request)
            subject = "Your OTP Code"

            # Sending mail to user

            message = f"Your one time Password is: {otp} "
            send_mail(subject, message,
                      "xloopokta@xloopdigital.com", [user.email])

            request.session["username"] = username
            return redirect("otp")

        else:
            try:
                user = User.objects.get(username=username)
                # Password is incorrect
                messages.error(
                    request, "Incorrect password. Please try again.")
            except User.DoesNotExist:
                # Username does not exist
                messages.error(request, "Username does not exist.")
            # Pass the error message to the template
            return render(request, "registration/sign-in.html", {})
    else:
        return render(request, "registration/sign-in.html", {})


def otp_view(request):
    # if request.user.is_authenticated:
    #     return redirect("home")

    error_message = None
    if request.method == "POST":
        otp = ""
        for i in range(1, 7):
            field_name = f"otp{i}"
            if field_name in request.POST:
                otp += request.POST[field_name]
            else:
                error_message = "Invalid OTP format."
                break

        username = request.session["username"]

        if "otp_secret_key" in request.session and "otp_valid_Date" in request.session:
            otp_secret_key = request.session["otp_secret_key"]
            otp_valid_until = request.session["otp_valid_Date"]

            if otp_secret_key and otp_valid_until is not None:
                valid_until = datetime.fromisoformat(otp_valid_until)

                if valid_until > datetime.now():
                    totp = pyotp.TOTP(otp_secret_key, interval=240)

                    # This line will help us to login to the application
                    if totp.verify(otp):
                        user = get_object_or_404(User, username=username)
                        login(request, user)

                        # return render(request, 'main/dashboard/dashboard.html')
                        return redirect("home")

                    else:
                        pass

                else:
                    pass
            else:
                pass

    return render(request, "registration/otp.html", {})


def login_user(request):
    pass


def logout_user(request):
    logout(request)
    messages.success(request, "You've Been Logged Out!")
    return redirect("home")


def register_user(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            # Access email from form's cleaned_data
            email = form.cleaned_data["email"]
            if User.objects.filter(email=email).exists():
                messages.error(request, "This email is already in use.")
                return redirect("register_user")

            username = form.cleaned_data["username"]
            password = form.cleaned_data["password1"]

            user = form.save(commit=False)
            user.is_email_verified = False
            user.is_active = False
            # To generate unique token
            user.email_verification_token = str(uuid.uuid4())
            user.save()

            email_verification = EmailVerification(
                user=user, token=user.email_verification_token
            )
            email_verification.save()

            current_site = get_current_site(request)
            subject = "Activate your Account"
            activation_link = f"http://{current_site.domain}/verify_email/{user.email_verification_token}/"

            message = f"Click the link to activate your account: {activation_link} "
            send_mail(subject, message,
                      "xloopokta@xloopdigital.com", [user.email])

            messages.success(
                request, "Your Account Has Been Created Successfully " + username
            )
            return render(request, "registration/verification_form.html")
        else:
            print("Form errors:", form.errors)  # Print form validation errors
    else:
        form = SignUpForm()  # Initialize an instance of SignUpForm
    return render(request, "registration/sign-up.html", {"form": form})


def verify_email_view(request, token):
    try:
        email_verification = get_object_or_404(
            EmailVerification, token=token, user__is_active=False
        )
        user = email_verification.user

        if user:
            user.is_email_verified = True
            user.email_verification_token = None
            user.is_active = True
            user.save()
            return redirect("home")

        # Check if the email is valid
        email = user.email
        if not re.match(r"^.+@.+\..+$", email):
            raise ValidationError("Invalid email format")

        user.is_email_verified = True
        user.is_active = True
        user.save()
        return redirect("home")

    except User.DoesNotExist:
        return HttpResponse("Activation Link is invalid")
    except ValidationError as e:
        return render(request, "registration/error.html", {"error_message": str(e)})


@login_required
def add_app(request):
    if not request.user.is_superuser:
        return redirect("app_dashboard")

    if request.method == "POST":
        # Include request.FILES to handle the uploaded image
        form = AppCreationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            # You might want to redirect to a different page after creating the app
            return redirect("user_list")
        else:
            messages.error(
                request, "Form submission failed. Please check the data you entered."
            )

    else:
        form = AppCreationForm()

    return render(request, 'main/dashboard/add_app.html', {'form': form})

@login_required
def user_list(request):
    if not request.user.is_superuser:
        return redirect("app_dashboard")

    # Query all users
    users = User.objects.all()

    return render(request, 'main/dashboard/tables.html', {'users': users})
 
@login_required
def edit_user(request, user_id):
    if not request.user.is_superuser:
        return redirect("app_dashboard")

    user = get_object_or_404(User, id=user_id)
    user_profile, created = UserProfile.objects.get_or_create(user=user)

    if request.method == "POST":
        form = UserAppAssignmentForm(
            request.POST, initial={"apps": user_profile.allowed_apps.all()}
        )
        if form.is_valid():
            apps = form.cleaned_data["apps"]
            if apps is None:  # Handle the case of no apps being selected
                apps = []  # Assign an empty list
            user_profile.allowed_apps.set(apps)
            user_profile.save()
            messages.success(request, "Apps updated successfully")
            return redirect("user_list")
        else:
            messages.error(
                request, "Form contains errors. Please check and try again.")
    else:
        form = UserAppAssignmentForm(
            initial={"apps": user_profile.allowed_apps.all()})

    # return render(request, "main/old/edit_user.html", {"form": form, "user": user})

    return render(request, 'main/dashboard/assign_user.html', {'form': form, 'user': user})
    # return render(request, 'main/old/edit_user.html', {'form': form, 'user': user})