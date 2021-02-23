import json
from django.db import models
from .models import User, Message, Chat, Participant
from channels.db import database_sync_to_async
from asgiref.sync import async_to_sync
from django.core import serializers

# saves sign up form into database
# input: form -> sign up form,
# contains username, password, first name, last name
def signup(form):
    form.save()
    # signup

# logins user into chatting app
# returns True if user exists given username and password
# returns False otherwise
# input: username_in -> username input
# input: password_in -> password input
def login(username_in, password_in):
    account = User.objects.filter(username = username_in, password = password_in)
    if account.exists():
        return True
    return False
    # login

# creates new chat given participants and current user
# input: participants_in -> participants to be in chat (aside from user creating chat)
# input: user -> (current) user creating chat
@database_sync_to_async
def add_chat(participants_in, user):
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
    # add_chat

# searches chatbase to see if (private) chat exists
# returns True if it exists, False otherwise
# input: participants_in -> array containing one participant in chat
# input: user -> (current) user searching for chat
@database_sync_to_async
def search_chatbase(participants_in, user):
    print(participants_in[0]['pk'])
    account = Chat.objects.filter(private=True).filter(participants__pk=participants_in[0]['pk']).filter(participants__pk=user.pk)
    if account.exists():
        return account[0]
    return False
    # search_chatbase

# adds messages being sent to database
# input: chat_pk -> primary key of chat
# input: user -> current user (scope from consumer class)
# input: msg -> content of message being sent
# input: img -> optional image inside message
# input: time -> time of being being sent
@database_sync_to_async
def send_message(chat_pk, user, msg, img, time):
    current_chat = Chat.objects.get(pk=chat_pk)
    message = Message.objects.create(
        sender = user,
        content = msg,
        image = img,
        timestamp = time
    )
    current_chat = Chat.objects.get(pk=chat_pk)
    current_chat.messages.add(message)
    current_chat.most_recent_time = time
    current_chat.save()
    return
    # send_message

# checks if there is a user in the database with a username 
# that starts with username being typed
# input: username -> username being searched
# input: user -> current user (scope from consumer class)
@database_sync_to_async
def search_userbase(username, user):
    searched_users = User.objects.filter(username__startswith=username).exclude(pk = user.pk)
    users_json = serializers.serialize('json', searched_users)
    return users_json
    # search_chatbase

# authenticates user
# checks if user is in database
# checks if user is a participant in chat given room
# input: username_in -> username of user (scope from consumer class)
# input: room -> current room (member of consumer class)
@database_sync_to_async
def authenticate(username_in, room):
    account = User.objects.filter(username = username_in)
    # in_chat = current_chat.check()
    if account.exists():
        current_chat = Chat.objects.filter(participants__pk=account[0].pk).filter(pk=room)
        if not current_chat.exists():
            return False
        print(account[0])
        return account[0]
    return False
    # authenticate

# returns user's chats ordered by most recent message in each chat
# input: user -> current user (scope from consumer class)
@database_sync_to_async
def get_chats(user):
    # Participant.objects.all().delete()
    # Chat.objects.all().delete()
    chats = Chat.objects.filter(participants__pk=user.pk).order_by("-most_recent_time")#.order_by("message_set__timestamp")##.order_by("messages__timestamp")#.order_by("-message__timestamp")
    #current_chats = chats.distinct("pk")
    chats_json = serializers.serialize('json', chats)
    loaded_chats = json.loads(chats_json)
    print(f'count: {chats}')
    sliced = user.username
    for chat in loaded_chats:
        print(chat['fields']['chat_name'].index(sliced))
        try:
            if chat['fields']['chat_name'].index(sliced + ", ") != -1:
                chat['fields']['chat_name'] = chat['fields']['chat_name'].replace(sliced + ",", "")
        except:
            print(chat['fields']['chat_name'].index(sliced))
            chat['fields']['chat_name'] = chat['fields']['chat_name'].replace(", " + sliced, "")
    
    # print(len(loaded_chats))
    # print(f'loaded chats: {loaded_chats}')
    return loaded_chats
    # get_chats

# gets chat messages given chat room
# input: room -> current room (member of consumer class)
@database_sync_to_async
def get_current_messages(room):
    # Participant.objects.all().delete()
    # Chat.objects.all().delete()
    print(f'room: {room}')
    try:
        current_chat = Chat.objects.get(pk=room)
        current_messages = current_chat.messages.all().order_by("-timestamp")
        #current_messages = current_chat.message_set.all().order_by("-timestamp")
        messages_json = serializers.serialize('json', current_messages[:20])
        loaded_messages = json.loads(messages_json)  
        
        return loaded_messages
    except:
        return False
        # get_current_messages

@database_sync_to_async
def grab_messages(room, num_loaded_messages):
    try:
        current_chat = Chat.objects.get(pk=room)
        current_messages = current_chat.messages.all().order_by("-timestamp")
        if num_loaded_messages >= len(current_messages):
            return
        to_load = num_loaded_messages * 2
        if to_load / 2 > 100:
            to_load = num_loaded_messages + 100
        if to_load > len(current_messages):
            to_load = len(current_messages)
        messages_json = serializers.serialize('json', current_messages[num_loaded_messages:to_load])
        num_loaded_messages = to_load
        loaded_messages = json.loads(messages_json)
        return loaded_messages
    except:
        return False 
        # grab_messages
 
# gets most recent messages in every chat
# input: user -> current user (scope from consumer class)
@database_sync_to_async
def get_top_messages(user):
    user_chats = Chat.objects.filter(participants__pk=user.pk).order_by("pk")
    ##print(f'old set of chats: {user_chats}')
    top_messages = []
    for chat in user_chats:
        queryset = chat.messages.all().order_by("-timestamp")
        if queryset.exists():
            top_messages.append(queryset[0])
            #print(f'top message of chat {chat.pk} is {queryset[0].content}')
        else:
            top_messages.append(None)
    return top_messages 
    # get_top_messages

# gets most recent messages in every chat
# compares them to current top messages to check for new messages
# returns any new messages
# input: user -> current user (scope from consumer class)
# input: top_messages -> current top_messages
@database_sync_to_async
def get_new_messages(user, top_messages):
    user_chats = Chat.objects.filter(participants__pk=user.pk).order_by("pk")
    #print(f'new set of chats: {user_chats}')
    new_top = []
    new_messages = []
    updated_chats = []
    for counter in range(0, len(top_messages)):
        chat = user_chats[counter]
        message = top_messages[counter]
        queryset = chat.messages.all().order_by("-timestamp")
        if not queryset.exists():
            new_top.append(None)
            continue
        latest = queryset[0]
        new_top.append(latest)
        #print(f'comparing latest: {latest.timestamp} at {latest.pk} to top: {message.timestamp} at {message.pk}')
        if latest.timestamp > message.timestamp:
            #message = serializers.serialize('json', latest)
            new_messages.append(latest)
            updated_chats.append(chat.pk)
    new_messages_json = serializers.serialize('json', new_messages)
    loaded_messages = json.loads(new_messages_json)
    #print(f'top messages: {top_messages}')
    #print(f'new messages: {loaded_messages}')
    return loaded_messages, updated_chats, new_top
    # get_new_messages
