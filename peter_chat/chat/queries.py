from .models import User, Message, Chat, Participant

def signup(username_in, password_in, first_name_in, last_name_in):
    user = User.objects.create(
        username=username_in,
        password=password_in,
        first_name=first_name_in,
        last_name=last_name_in,
    )

def login(username_in, password_in):
    account = User.objects.filter(username = username_in, password = password_in)
    if account.exists():
        return account
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
