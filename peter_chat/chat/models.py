from django.db import models

# User model
class User(models.Model):
    username = models.CharField(max_length=20, primary_key=True)
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
    #chats = models.ManyToManyField(UserChat)
    friends = models.ManyToManyField('self')

    def __status__(self):
        return self.Status.label

    def __username__(self):
        return self.username

    def __name__(self):
        return self.first_name + " " + self.last_name


# Message model
class Message(models.Model):
    content = models.TextField()
    image = models.ImageField(upload_to='message_images/', blank=True)
    sender = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

# Chat model
class Chat(models.Model):
    participates = models.ManyToManyField(User, related_name='chats')
    messages = models.ManyToManyField(Message, blank=True)
    private = models.BooleanField(default=True)

    def __str__(self):
        return "{}".format(self.pk)
'''
# Model for a user reference to a chat
class UserChat(models.Model):
    chat = models.ForeignKey(Chat, on_delete = models.CASCADE)
    notifications = BooleanField(default=True)
    favorite = BooleanField(default=False)'''
