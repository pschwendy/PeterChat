import json
from datetime import datetime
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.auth import login
from .queries import search_userbase, authenticate, search_chatbase, add_chat, get_chats, send_message, get_current_messages, get_top_messages, get_new_messages, grab_messages, json_load_top_messages, authenticate_inbox, get_full_name
from channels.db import database_sync_to_async
import time
import threading
import asyncio
from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name
        #self.messages = await get_current_messages(self.room_name)
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        

    async def disconnect(self, close_code):
        # Leave room group
        #print("DONE")
        self.disconnected = True
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def send_for_updates(self):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'update_chats',
            }
        )
    def start_updates(self):
        #print("CONNECTED")
        while True:
            if self.disconnected:
                #print('...........disconnecting thread.........')
                break
            # #print("running...")
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            loop.run_until_complete(self.send_for_updates())
            loop.close()

            time.sleep(0.5)

    # Receive message from WebSocket
    async def receive(self, text_data):
        data_json = json.loads(text_data)
        receive_type = data_json['send_type']
        if receive_type == 'chat_message':
            message = data_json['message']
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                }
            )
        elif receive_type == 'fetch_messages':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'fetch_messages',
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
            #print("authenticating...")
            user_login = data_json['username']
            user = await authenticate(user_login, self.room_name)
            await login(self.scope, user)
            await database_sync_to_async(self.scope["session"].save)()
            self.top_messages, chats_by_pk = await get_top_messages(user)
            #print(f"chats by pk: {chats_by_pk}")
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'get_user_chats',
                    'chat_list': chats_by_pk
                }
            )
            self.disconnected = False
            thread = threading.Thread(target=self.start_updates)
            thread.start()

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        sending_message = await send_message(self.room_name, self.scope['user'], message, None, datetime.now())
        #await send_message(self.room_name, self.scope['user'], message, None, datetime.now())
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'send_type': 'chat',
            'message': sending_message,
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
        #print()
        #print(f"participants: {participants}")
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
        self.num_loaded_messages = 20
        ##print("HI!")
        pk = self.scope["user"].pk
        chats_by_pk = event['chat_list']
        #print(f'top again: {self.top_messages}')
        top_messages = await json_load_top_messages(self.top_messages, chats_by_pk)
        full_name = await get_full_name(pk)
        await self.send(text_data=json.dumps({
            'send_type': 'load',
            'chats': chats,
            'messages': messages,
            'top_messages': top_messages,
            'pk': pk,
            'name': full_name
        }))

    async def get_chat_messages(self, event):
        #print('yo')
        messages = await get_current_messages(self.room_name)
        #print('yoyo')
        #self.message_history = history
        
        #print(f'num loaded messages: {self.num_loaded_messages}')
        pk = self.scope["user"].pk
        #print("...sending messages")
        await self.send(text_data=json.dumps({
            'send_type': 'load_messages',
            'messages': messages,
            'pk': pk
        }))

    async def fetch_messages(self, event):
        message_history, self.num_loaded_messages = await grab_messages(self.room_name, self.num_loaded_messages)
        pk = self.scope["user"].pk
        if message_history == False or message_history == None:
            return
        await self.send(text_data=json.dumps({
            'send_type': 'load_messages',
            'messages': message_history,
            'pk': pk
        }))

    async def update_chats(self, event):
        new_messages, updated_chats, new_top = await get_new_messages(self.scope['user'], self.top_messages)
        self.top_messages = new_top
        if len(new_messages) > 0:
            #print(f'sending {new_messages} and {updated_chats}')
            await self.send(text_data=json.dumps({
                'send_type': 'new_messages',
                'messages': new_messages,
                'pks': updated_chats
            }))


class InboxConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_pk = self.scope['url_route']['kwargs']['user_number']
        self.room_group_name = 'user_%s' % self.user_pk
        #self.messages = await get_current_messages(self.room_name)
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'authenticate_user',
                }
            )
        await self.accept()
        

    async def disconnect(self, close_code):
        # Leave room group
        #print("DONE")
        self.disconnected = True
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def send_for_updates(self):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'update_chats',
            }
        )
    def start_updates(self):
        #print("CONNECTED")
        while True:
            if self.disconnected:
                #print('...........disconnecting thread.........')
                break
            # #print("running...")
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            loop.run_until_complete(self.send_for_updates())
            loop.close()

            time.sleep(0.5)
    
    # Receive message from WebSocket
    async def receive(self, text_data):
        data_json = json.loads(text_data)
        receive_type = data_json['send_type']
        if receive_type == 'search':
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
        """elif receive_type == 'authenticate':
            #print("authenticating...")
            user_login = data_json['username']
            user = await authenticate(user_login, self.room_name)
            await login(self.scope, user)
            await database_sync_to_async(self.scope["session"].save)()"""

    async def authenticate_user(self, event):
        user = await authenticate_inbox(self.user_pk)
        await login(self.scope, user)
        await database_sync_to_async(self.scope["session"].save)()
        self.top_messages, chats_by_pk = await get_top_messages(user)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'get_user_chats',
                'chat_list': chats_by_pk
            }
        )
        self.disconnected = False
        thread = threading.Thread(target=self.start_updates)
        thread.start()
    
    async def get_user_chats(self, event):
        chats = await get_chats(self.scope["user"])
        chats_by_pk = event['chat_list']
        top_messages = await json_load_top_messages(self.top_messages, chats_by_pk)
        full_name = await get_full_name(self.user_pk)
        #print(f"SENDING THESE TOP MESSAGES: {top_messages}")
        await self.send(text_data=json.dumps({
            'send_type': 'load',
            'chats': chats,
            'top_messages': top_messages,
            'pk': self.user_pk,
            'name': full_name
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
        #print()
        #print(f"participants: {participants}")
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

    async def update_chats(self, event):
        new_messages, updated_chats, new_top = await get_new_messages(self.scope['user'], self.top_messages)
        self.top_messages = new_top
        if len(new_messages) > 0:
            #print(f'sending {new_messages} and {updated_chats}')
            await self.send(text_data=json.dumps({
                'send_type': 'new_messages',
                'messages': new_messages,
                'pks': updated_chats
            }))
    