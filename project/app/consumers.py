import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async
from .models import ChatRoom, Message

User = get_user_model()

class ChatRoomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_box_name = self.scope["url_route"]["kwargs"]["chat_box_name"]
        self.group_name = "chat_%s" % self.chat_box_name

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    # This function receives messages from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        username = text_data_json["username"]
        file_url = text_data_json.get("file_url", None) 
        file_name = text_data_json.get("file_name", "")
        # Save the encrypted message to the database
        await self.save_message(username, self.chat_box_name, message,file_url,file_name)

        # Send the message to the group
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "chatbox_message",
                "message": message,
                "username": username,
                "file_url": file_url,
                "fileName": file_name
            }
        )

    # Receive message from room group
    async def chatbox_message(self, event):
        message = event["message"]
        username = event["username"]
        file_url = event.get("file_url",None)
        file_name = event.get("fileName", "")

        # Send message and username of sender to WebSocket
        await self.send(
            text_data=json.dumps(
                {
                    "message": message,
                    "username": username,
                    "file_url": file_url,
                    "fileName": file_name
                }
            )
        )

    @sync_to_async
    def save_message(self, username, room_name, message,file_url,file_name=None):
        user = User.objects.get(username=username)
        room = ChatRoom.objects.get(name=room_name)
        # Create a new message (the encryption happens in the model's save method)
        message_instance = Message.objects.create(room=room, user=user, encrypted_message=message)

        # Handle file saving if a file URL is provided
        if file_url:
            # You can adjust how you save the file based on your requirements
            message_instance.file = file_url
            message_instance.file_name=file_name  # Assuming `file` is a field in your Message model
            message_instance.save()