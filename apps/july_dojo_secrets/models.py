from __future__ import unicode_literals

from django.db import models

# Create your models here.
import md5
import bcrypt
import os, binascii

# Create your models here.

import re
NAME_REGEX =re.compile('^[A-z]+$')
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

class UserManager(models.Manager):
    def login(self, postData):
        messages = []
        email = postData['email']
        password = postData['password']
        if len(str(email)) < 1:
            messages.append("email must not be blank!")
        if len(str(email)) < 2:
            messages.append("email must be at least 2 characters long!")
        if len(str(password)) < 1:
            messages.append("password must not be blank")
        if len(str(password)) < 8:
            messages.append("password must be at least 8 characters long!")
        if User.objects.filter(email=email):
            # encode the password to a specific format since the above email is registered
            login_pw = password.encode()
            # encode the registered user's password from database to a specific format
            db_pw = User.objects.get(email=email).password.encode()
            # compare the password with the password in database
            if not bcrypt.checkpw(login_pw, db_pw):
                messages.append("Password is Incorrect!")
        else:
            messages.append("Email has already been registered!")
        return messages

    def register(self, postData):
            print "register process"
            messages = []
            first_name = postData['first_name']
            if len(str(first_name)) < 1:
                messages.append("Error! First name must not be blank!")
            if len(str(first_name)) < 2:
                messages.append("Error! First name must be at least 2 characters long!")

            last_name = postData['last_name']
            if len(str(last_name)) < 1:
                messages.append("Error! Last name must not be blank!")
            if len(str(last_name)) < 2:
                messages.append("Error! Last name must be at least 2 characters long!")

            email = postData['email']
            if len(str(email)) < 1:
                messages.append("Error! Email must not be blank!")
            if len(str(email)) < 2:
                messages.append("Error! Email must be at least 2 characters long!")
            if not EMAIL_REGEX.match(email):
                messages.append("Error! Email must be in a valid format!")

            password = postData['password']
            if len(str(password)) < 1:
                messages.append("Error! Password must not be blank!")
            if len(str(password)) < 8:
                messages.append("Error! Password must be at least 8 characters long!")

            pw_confirm = postData['pw_confirm']
            if pw_confirm != password:
                messages.append("Error! Passwords must match!")

            user_list = User.objects.filter(email=email)
            for user in user_list:
                print user.email
            if user_list:
                messages.append("Error! Email is already in the system!")
            if not messages:
                print "No messages"
                password = password.encode()
                salt = bcrypt.gensalt()
                hashed_pw = bcrypt.hashpw(password, salt)
                # password = password
                print "Create User"
                print hashed_pw
                User.objects.create(first_name=first_name, last_name=last_name, email=email, password=hashed_pw)
                print hashed_pw
                print User.objects.all()
                return None
            return messages

class SecretManager(models.Manager):
    def validate(self, postedSecret, userid):
        if len(postedSecret) < 4:
            return(False, "Secrets must be at least 4 characters long")
        try:
            currentuser = User.objects.get(id=userid)
            self.create(secret=postedSecret, author=currentuser)
            return(True, "Your secret is safe with us")
        except:
            return(False, "We could not create this secret at this time")

    def newlike(self, secretid, userid):
        try:
            secret = self.get(id=secretid)
        except:
            return(False, "This secret is not found in our database")
        user = User.objects.get(id=userid)
        if secret.author == user:
            return(False, "Shame on you! You shouldn't like your own secrets!")
        secret.likers.add(user)
        return(True, "You liked this secret!")

    def deleteLike(self, secretid, userid):
        try:
            secret = self.get(id=secretid)
        except:
            return(False, "This secret is not found in our database")
        user = User.objects.get(id=userid)
        if secret.author != user:
            return(False, "Shame on you! You can't delete other people's secrets!")
        secret.delete()
        return(True, "Secret Deleted!")
class User(models.Model):
    first_name = models.CharField(max_length=45)
    last_name = models.CharField(max_length=45)
    email = models.CharField(max_length=45)
    password = models.CharField(max_length=45)
    pw_confirm = models.CharField(max_length=45)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = UserManager()

    def __unicode__(self):
        return "First Name: " + str(self.first_name) + ", Last Name: " + str(self.last_name) + ", Email: " + str(self.email) + ", Password: " + str(self.password)

class Secret(models.Model):
    secret = models.CharField(max_length=400)
    author = models.ForeignKey(User)
    likers = models.ManyToManyField(User, related_name="likedsecrets")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = SecretManager()
