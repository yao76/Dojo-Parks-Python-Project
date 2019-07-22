from django.db import models
from django.core.validators import re
from datetime import date
from django.utils.dateparse import parse_date, parse_time
import bcrypt
import requests


class UserManager(models.Manager):
    def register_validator(self, postData):
        errors = {}
        passcapital = re.compile(r'[A-Z]')
        passlower = re.compile(r"[a-z]")
        passspecial = re.compile(r"[@_!#$%^&*()<>?/|}{~:]")
        first_name = postData["first_name"]
        last_name = postData["last_name"]
        email = postData["email"]
        password = postData["password"]
        password_confirm = postData["password_confirm"]
        if len(first_name) < 3 or len(first_name) > 50:
            errors["first_name"] = "First name must be between 3 - 50 characters"
        if len(last_name) < 3 or len(last_name) > 50:
            errors["last_name"] = "Last name must be between 3 - 50 characters"
        if re.search("[a-zA-Z0-9!#$%&'*+-/=?^_`{|}~]@.+[.]..+", email) is None:
            errors["email"] = "Email is invalid, try again"
        if len(password) < 8 or len(password) > 20:
            errors["passlength"] = "Password must be between 8 - 20 characters"
        if len(passspecial.findall(password)) == 0:
            errors["passspecial"] = "Password must contain at least 1 special character"
        if len(passcapital.findall(password)) == 0:
            errors["passcapital"] = "Password must contain at least 1 uppercase character"
        if len(passlower.findall(password)) == 0:
            errors["passlower"] = "Password must contain at least 1 lowercase character"
        if password != password_confirm:
            errors["password"] = "Passwords don't match, try again"
        return errors

    def login_validator(self, postData):
        errors = {}
        email = postData["email"]
        password = postData["password"]
        users = User.objects.filter(email=email)
        if len(users) == 0:
            errors["noemail"] = "That email isn't registered"
        elif not bcrypt.checkpw(password.encode(), users[0].password.encode()):
            errors["wrongpassword"] = "Password doesn't match"
        return errors



class User(models.Model):
    first_name = models.CharField(max_length=45)
    last_name = models.CharField(max_length=45)
    email = models.CharField(max_length=180)
    password = models.CharField(max_length=90)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = UserManager()

