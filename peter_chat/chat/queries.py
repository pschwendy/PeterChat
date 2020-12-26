from models import User, Message, Chat, Participant

def add_user(username_in, password_in, first_name_in, last_name_in):
    user = User.objects.create(
        username=username_in,
        password=password_in,
        first_name=first_name_in,
        last_name=last_name_in,
    )

def add_chat(participants_in):
    chat_create = Chat.objects.create()
    if len(participants_in) > 2:
        chat_create.object.get(private=False)
    for user_in in participants_in:
        chat_create.object.participants.add(user_in)
    chat_create.save()
    for user_in in participants_in:
        participant = Participant(user = user_in, chat = chat_create)
        particpant.save()

def send_message(current_chat, user, msg, img, time):
     message = Message.objects.create(
        sender = user,
        content = msg,
        image = img,
        timestamp = time
    )
    current_chat.messages.add(message)
    current_chat.save()
