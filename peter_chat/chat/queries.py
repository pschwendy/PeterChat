from .models import User, Message, Chat, Participant
from channels.db import database_sync_to_async
from asgiref.sync import async_to_sync
from django.core import serializers

def signup(form):
    form.save()

def login(username_in, password_in):
    account = User.objects.filter(username = username_in, password = password_in)
    if account.exists():
        return True
    return False

def add_chat(participants_in):
    chat_create = Chat()
    if len(participants_in) > 2:
        chat_create.object.update(private=False)
    chat_create.object.participants.add(user_in for user_in in participants_in)
    chat_create.save()
    participant = Participant.objects.create(user = (user_in for user_in in participants_in), chat = chat_create)

def send_message(current_chat, user, msg, img, time):
    message = Message.objects.create(
        sender = user,
        content = msg,
        image = img,
        timestamp = time
    )
    current_chat.messages.add(message)
    current_chat.save()

@database_sync_to_async
def search_userbase(username):
    searched_users = []
    for user in User.objects.filter(username__contains=username):
        searched_users.append(user)
    users_json = serializers.serialize('json', searched_users, fields=('username', 'first_name', 'last_name'))
    return users_json