from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
import datetime

from .models import User, Post, Profile, Following
from .forms import PostForm


def index(request):
    #Create modelForm for new posts; pass to template via context
    now = datetime.datetime.now()
    newPostForm = PostForm(initial = {'owner': request.user, 'likes': 0, 'timestamp': now})

    #Retrieve all posts to be rendered in template; order reverse chronologically; pass to template via context
    posts = Post.objects.all()
    posts = posts.order_by("-timestamp").all()
    context = {'form': newPostForm, 'posts': posts}

    return render(request, "network/index.html", context)

def create_post(request):
    #Retrieve form from template; check for validity; create Post object
    if request.method == "POST":
        #Used for 'initial' values
        user = request.user
        now = datetime.datetime.now()

        newPostForm = PostForm(request.POST, initial={'owner': user.id, 'likes': 0, 'timestamp': now})
        if newPostForm.is_valid():
            newPost = newPostForm.save()

    return HttpResponseRedirect(reverse("index"))

def profile_page(request, username):
    isFollowing = False

    #Retrieve ID for requested user
    user = User.objects.get(username = username)
    userID = user.id

    #Retrieve profile page/posts for the requested user
    profile = Profile.objects.get(user = userID)
    posts = Post.objects.filter(owner = userID)
    posts = posts.order_by("-timestamp").all()

    #Is the request being made by a registered user? If so, are they following the requested user?
    if (request.user.is_authenticated):
        registeredUser = User.objects.get(username = request.user.username)
        registeredUserID = registeredUser.id
        if (Following.objects.filter(followingUser = registeredUserID, followedUser = userID).exists()):
            isFollowing = True

    #Store in context and render profile page
    context = {"profile": profile, "posts": posts, "isFollowing": isFollowing}
    return render(request, "network/profile.html", context)

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
