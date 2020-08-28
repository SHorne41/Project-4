from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    numFollowers = models.IntegerField(default = 0)
    numFollowing = models.IntegerField(default = 0)

class Post(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.CharField(max_length = 280)
    likes = models.IntegerField(default = 0)
    timestamp = models.DateTimeField()


class Following(models.Model):
    followingUser = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followers")
    followedUser = models.ForeignKey(User, on_delete=models.CASCADE)
