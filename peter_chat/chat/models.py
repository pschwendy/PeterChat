from django.db import models
import datetime
from django.db.models import F
# User model
class User(models.Model):
    username = models.CharField(max_length=20, unique=True)
    password = models.CharField(max_length=30)
    first_name = models.CharField(max_length=32)
    last_name = models.CharField(max_length=40)
    on_delete=models.CASCADE
    class Status(models.TextChoices):
        ACTIVE = 'A', ('Active')
        IDLE = 'I', ('Idle')
        OFFLINE = 'O', ('Offline')
    status = models.CharField(
        max_length=1,
        choices=Status.choices,
        default=Status.ACTIVE,
    )
    profile_picture = models.ImageField(upload_to='profile_pictures/')
    friends = models.ManyToManyField('self')
    last_login = models.DateField(default=datetime.date(2020, 12, 10))
   # def __str__(self):
    #    return self.username

    def get_status(self):
        return self.Status.label

    def get_name(self):
        return self.first_name + " " + self.last_name

# Message model
class Message(models.Model):
    sender = models.ForeignKey(User, on_delete = models.CASCADE)
    #chat = models.ForeignKey(Chat, on_delete = models.CASCADE, default=1)
    content = models.TextField()
    image = models.ImageField(upload_to='message_images/', blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

# Chat model
class Chat(models.Model):
    chat_name = models.CharField(max_length=50, null=True)
    participants = models.ManyToManyField(User, related_name='chats', through='Participant')
    messages = models.ManyToManyField(Message, blank=True)
    private = models.BooleanField(default=True)
    most_recent_time = models.DateTimeField(auto_now=True)
    #class Meta:
    #    order_with_respect_to = ['messages__timestamp']
    def __str__(self):
        return "{}".format(self.pk)

# Model governing user relationship to a chat
class Participant(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    chat = models.ForeignKey(Chat, on_delete = models.CASCADE)
    notifications = models.BooleanField(default=True)
    favorite = models.BooleanField(default=False)
