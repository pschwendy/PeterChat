from django.db import models

# User model
class User(models.Model):
    username = models.CharField(max_length=20, primary_key=True)
    password = models.CharField(max_length=30)
    first_name = models.CharField(max_length=32)
    last_name = models.CharField(max_length=40)
    on_delete=models.CASCADE
    profile_picture = models.ImageField(upload_to='profile_pictures/')
    chats = models.ManyToManyField(UserChat)
    friends = models.ManyToManyField(User)

# Model for a user reference to a chat
class UserChat(models.Model):
    chat = models.ForeignKey(Chat)
    notifications = BooleanField(default=True)
    favorite = BooleanField(default=False)

# Chat model
class Chat(models.Model):
    users = models.ManyToManyField(User)
    messages = models.ManyToManyField(Message, blank=True))
    private = models.BooleanField(default=True)

# Message model
class Message(models.Model):
    content = models.TextField()
    image = models.ImageField(upload_to='message_images/', blank=True)
    sender = models.IntField()
    timestamp = models.DateTimeField(auto_now_add=True)

# Create your models here.
