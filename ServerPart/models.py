from django.db import models
from django.contrib.auth.models import User


class UserInfo(models.Model):
    info = models.CharField(max_length=500, null=False, default=" ")
    user = models.OneToOneField(to=User, on_delete=models.SET_NULL, null=True)


class Avatar(models.Model):
    img = models.ImageField(
        upload_to='pictures/',
        default='../static/img/default.jpg'
    )
    user_id = models.IntegerField()


class UserIp(models.Model):
    last_ip = models.CharField(max_length=15, null=False)
    user = models.ForeignKey(
        to=User,
        on_delete=models.SET_NULL,
        null=True
    )


class Task(models.Model):
    name = models.CharField(max_length=200, null=False)
    date_created = models.DateTimeField(null=False)
    author = models.ForeignKey(to=User, default=1, on_delete=models.SET_NULL, null=True)
    img_amount = models.IntegerField(default=1, null=False)
    description = models.TextField(max_length=100, null=True)
    is_done = models.BooleanField(default=False)
    deadline = models.DateTimeField(null=True)
    
    
class Images(models.Model):
    img = models.ImageField(upload_to='pictures/')
    task = models.ForeignKey(to=Task, on_delete=models.SET_NULL, null=True)


class Comments(models.Model):
    task_id = models.IntegerField()
    comment_text = models.CharField(max_length=10000)
    avatar = models.ForeignKey(to=Avatar, on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, null=True)


class Developer(models.Model):
    task = models.ForeignKey(to=Task, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, null=True)
    date_created = models.DateTimeField(null=True)
