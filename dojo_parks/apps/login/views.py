from django.shortcuts import render, redirect
from .models import User
from django.contrib import messages
import bcrypt


def index(request):
    if "user_id" in request.session:
        return redirect("parks/")
    else:
        return render(request, "login/index.html")


def register(request):
    errors = User.objects.register_validator(request.POST)
    if len(errors) > 0:
        for key, value in errors.items():
            messages.error(request, value, extra_tags=key)
        return redirect("/")
    else:
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        email = request.POST["email"]
        password = request.POST["password"]
        hashedpass = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        User.objects.create(first_name=first_name, last_name=last_name, email=email, password=hashedpass)
        request.session["user_id"] = User.objects.last().id
        return redirect("parks/")


def validate_login(request):
    errors = User.objects.login_validator(request.POST)
    if len(errors) == 0:
        user = User.objects.get(email=request.POST['email'])
        request.session["user_id"] = user.id
        return redirect("/parks/")
    else:
        for key, value in errors.items():
            messages.error(request, value, extra_tags=key)
        return redirect("/")


def logout(request):
    request.session.clear()
    return redirect('/')
