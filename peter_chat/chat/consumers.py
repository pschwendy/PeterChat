import json
from datetime import datetime
#from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.auth import login
from .queries import search_userbase, authenticate, search_chatbase, add_chat, get_chats, send_message, get_current_messages
from channels.db import database_sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        data_json = json.loads(text_data)
        receive_type = data_json['send_type']
        if receive_type == 'chat_message':
            message = data_json['message']
            await send_message(self.room_name, self.scope['user'], message, None, datetime.now())
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                }
            )
        elif receive_type == 'search':
            searched = data_json['username_searched']
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'search',
                    'searched': searched,
                }
            )
        elif receive_type == 'find_create':
            participants = data_json['participants']
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'find_chat',
                    'participants': participants,
                }
            )
        elif receive_type == 'authenticate':
            user_login = data_json['username']
            user = await authenticate(user_login)
            await login(self.scope, user)
            await database_sync_to_async(self.scope["session"].save)()
            print("HI!")
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'get_user_chats'
                }
            )
            
        

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        await send_message(self.room_name, self.scope['user'], message, None, datetime.now())
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'send_type': 'chat',
            'message': message,
            'sender': self.scope['user'].username
        }))

    async def search(self, event):
        searched = event['searched']
        searched_users = await search_userbase(searched, self.scope["user"])
        actual = json.loads(searched_users)
        await self.send(json.dumps({
            'send_type':'search',
            'users': json.dumps(actual)
        }))

    async def find_chat(self, event):
        participants = event['participants']
        print()
        print(f"participants: {participants}")
        if len(participants) > 1:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'create_chat',
                    'participants': participants,
                }
            )
            return

        found_chat = await search_chatbase(participants, self.scope["user"])
        if found_chat == False:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'create_chat',
                    'participants': participants,
                }
            )
        else:
            await self.send(json.dumps({
                'send_type':'switch',
                'chat':json.dumps(found_chat.pk)
            }))

    async def create_chat(self, event):
        participants = event['participants']

        # participants.append(self.scope["user"])
        created_chat = await add_chat(participants, self.scope["user"])
        await self.send(json.dumps({
            'send_type':'switch',
            'chat':json.dumps(created_chat.pk)
        }))

    async def get_user_chats(self, event):
        chats = await get_chats(self.scope["user"])
        messages = await get_current_messages(self.room_name)
        print("HI!")
        await self.send(text_data=json.dumps({
            'send_type': 'load',
            'chats': chats,
            'messages': messages
        }))