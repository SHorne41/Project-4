from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.http import JsonResponse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
import json
import datetime

from .models import User, Post, Following
from .forms import PostForm, FollowForm


def index(request):
    #Create modelForm for new posts; pass to template via context
    now = datetime.datetime.now()
    newPostForm = PostForm(initial = {'owner': request.user, 'likes': 0, 'timestamp': now})

    #Retrieve all posts to be rendered in template; order reverse chronologically
    posts = Post.objects.all()
    posts = posts.order_by("-timestamp").all()

    #Create pagination object for posts
    paginator = Paginator(posts, 10)                    #Display 10 posts per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {"form": newPostForm, "title": "All Posts", 'page_obj': page_obj}

    return render(request, "network/index.html", context)

@csrf_exempt
def updateLikes(request):
    if request.method == "PUT":
        #Retrieve pertinent information from request
        data = json.loads(request.body)
        owner = data.get("owner")
        postContent = data.get("postContent")
        newLikeCount = data.get("newLikeCount")

        #Retrieve the appropriate userID
        userID = User.objects.get(username = owner).pk

        #Retrieve the post to be updated; update with new content
        post = Post.objects.get(owner = userID, content = postContent)
        post.likes = newLikeCount
        post.save()

        return JsonResponse({"message": "Post updated successfully"}, status=201)

    else:
        return JsonResponse({"error": "POST request required."}, status=400)

@csrf_exempt
def editPost(request):
    if request.method == "PUT":
        #Retrieve pertinent information from request
        data = json.loads(request.body)
        owner = data.get("owner")
        postContent = data.get("postContent")
        updatedContent = data.get("updatedContent")

        #Retrieve the appropriate userID
        userID = User.objects.get(username = owner).pk

        #Retrieve the post to be updated; update with new content
        post = Post.objects.get(owner = userID, content = postContent)
        post.content = updatedContent
        post.save()

        return JsonResponse({"message": "Post updated successfully"}, status=201)

    else:
        return JsonResponse({"error": "POST request required."}, status=400)

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
    #Retrieve requested user & their posts
    user = User.objects.get(username = username)
    userID = user.id
    posts = Post.objects.filter(owner = userID)
    posts = posts.order_by("-timestamp").all()

    #Used for context
    isFollowing = False
    newFollowForm = FollowForm(initial={'followingUser': request.user.id, 'followedUser': userID})

    #Is the request being made by a registered user? If so, are they following the requested user?
    if (request.user.is_authenticated):
        registeredUser = User.objects.get(username = request.user.username)
        registeredUserID = registeredUser.id
        if (Following.objects.filter(followingUser = registeredUserID, followedUser = userID).exists()):
            isFollowing = True

    #Store in context and render profile page
    context = {"profile": user, "posts": posts, "isFollowing": isFollowing, "form": newFollowForm}
    return render(request, "network/profile.html", context)

def follow(request, username):
    #Retrieve user/profile to be followed
    followedUser = User.objects.get(username = username)
    userID = followedUser.id

    #Retrieve user who's following
    followingUser = User.objects.get(username = request.user.username)

    #Check for form validity. If true, create new Following object
    if request.method == "POST":
        newFollowForm = FollowForm(request.POST, initial={'followingUser': request.user.id, 'followedUser': userID})
        if newFollowForm.is_valid():
            newFollow = newFollowForm.save()

            #Update followers/following for users involved
            followingUser.numFollowing += 1
            followingUser.save()
            followedUser.numFollowers += 1
            followedUser.save()


    return HttpResponseRedirect(reverse("index"))

def unfollow(request, username):
    #Retrieve users involved
    followedUser = User.objects.get(username = username)
    followingUser = User.objects.get(username = request.user.username)

    #Retrive all users the followingUser is following
    following = Following.objects.filter(followingUser = request.user.id)

    #Search for user to unfollow
    for user in following:
        if (user.followedUser == User.objects.get(username = username)):
            #Unfollow user
            unfollowObject = user
            unfollowObject.delete()

            #Update followers/following for users involved
            followingUser.numFollowing -= 1
            followingUser.save()
            followedUser.numFollowers -= 1
            followedUser.save()

    return HttpResponseRedirect(reverse("index"))

def following(request):
    #Used in context; will contain all posts
    postIDs = []

    #Retrieve all users the current user is following
    following = Following.objects.filter(followingUser = request.user.id)

    #Retrieve all postIDs for posts of each user followed
    for user in following:
        temp = Post.objects.filter(owner = user.followedUser)
        for post in temp:
            postIDs.append(post.pk)

    #Retrieve all posts using postIDs; sort based on timestamp
    posts = Post.objects.filter(id__in = postIDs)
    posts = posts.order_by("-timestamp").all()

    #Create pagination object for posts
    paginator = Paginator(posts, 10)                    #Display 10 posts per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {"title": "Following", 'page_obj': page_obj}

    return render(request, "network/index.html", context)

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
