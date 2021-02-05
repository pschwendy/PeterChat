import json
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

@database_sync_to_async
def add_chat(participants_in, user):
    # plz work
    name = ""
    chat_create = Chat()
    if len(participants_in) > 2:
        chat_create.private = False

    chat_create.save()
    for user_in in participants_in:
        add_user = User.objects.get(id=user_in["pk"])
        chat_create.participants.add(add_user)
        name += add_user.username + ", "
        print(f'adding user: {add_user}')
    this_user = User.objects.get(id=user.pk)
    chat_create.participants.add(this_user)
    name += this_user.username
    chat_create.chat_name = name
    chat_create.save()

    return chat_create

@database_sync_to_async
def search_chatbase(participants_in, user):
    print(participants_in[0]['pk'])
    try:
        account = Chat.objects.filter(private=True).filter(participants__pk=participants_in[0]['pk'])
        print(account[0])
    except:
        print("Query not allowed")
    if account.exists():
        print("returning account")
        return account[0]
    print("hello")
    return False

@database_sync_to_async
def send_message(chat_pk, user, msg, img, time):
    message = Message.objects.create(
        sender = user,
        content = msg,
        image = img,
        timestamp = time
    )
    current_chat = Chat.objects.get(pk=chat_pk)
    current_chat.messages.add(message)
    current_chat.save()

@database_sync_to_async
def search_userbase(username, user):
    searched_users = User.objects.filter(username__startswith=username).exclude(pk = user.pk)
    users_json = serializers.serialize('json', searched_users)
    return users_json

@database_sync_to_async
def authenticate(username_in):
    account = User.objects.filter(username = username_in)
    if account.exists():
        print(account[0])
        return account[0]
    return False

@database_sync_to_async
def get_chats(user):
    #Participant.objects.all().delete()
    ##Chat.objects.all().delete()
    chats = Chat.objects.filter(participants__pk=user.pk).order_by("-messages__timestamp")
    chats_json = serializers.serialize('json', chats)
    loaded_chats = json.loads(chats_json)
    for chat in loaded_chats:
        sliced = user.username
        try:
            if chat['fields']['chat_name'].index(sliced + ", "):
                chat['fields']['chat_name'] = chat['fields']['chat_name'].replace(sliced + ", ", "")
        except:
            chat['fields']['chat_name'] = chat['fields']['chat_name'].replace(", " + sliced, "")
             
    #participants = Chat.participants.all()
    #print("NAME")
    #print(chats_json)
    print(len(loaded_chats))
    return loaded_chats

@database_sync_to_async
def get_current_messages(room):
    #Participant.objects.all().delete()
    #Chat.objects.all().delete()
    try:
        current_chat = Chat.objects.get(pk=room)
        current_messages = current_chat.messages.all().order_by("-timestamp")
        messages_json = serializers.serialize('json', current_messages[:200])
        loaded_messages = json.loads(messages_json)  
        print(f'room: {room}')
        print(loaded_messages)
        return loaded_messages
    except:
        return False    
    #participants = Chat.participants.all()
    #print("NAME")
    #print(chats_json)
    