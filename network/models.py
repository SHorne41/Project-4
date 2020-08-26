from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Post(models.Model):
    owner = models.ForeignKey(User, on_delete = models.CASCADE)
    content = models.CharField(max_length = 280)
    likes = models.IntegerField(default = 0)
    timestamp = models.DateTimeField()
