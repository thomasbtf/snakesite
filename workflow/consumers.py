from asgiref.sync import async_to_sync
from channels.consumer import SyncConsumer
from channels.generic.websocket import AsyncWebsocketConsumer

class RunMessageConsumer(SyncConsumer):
    def websocket_connect(self, event):
        group_name = self.scope["url_route"]["kwargs"]["run_id"]

        self.send(
            {
                "type": "websocket.accept",
            }
        )

        # Join group
        print("Consumer joined run message group", group_name)
        async_to_sync(self.channel_layer.group_add)(group_name, self.channel_name)

    def websocket_disconnect(self, event):

        # Leave  group
        group_name = self.scope["url_route"]["kwargs"]["run_id"]
        async_to_sync(self.channel_layer.group_discard)(group_name, self.channel_name)

    def new_message(self, event):
        to_sent = {
            "type": "websocket.send",
            "text": event["content"],
        }
        self.send(to_sent)


class AsyncRunStatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.channel_group_name = "".join(["status_", self.scope["url_route"]["kwargs"]["run_id"]])

        # Join the group
        await self.channel_layer.group_add(
            self.channel_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave the group
        await self.channel_layer.group_discard(
            self.channel_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data=None, bytes_data=None):
        pass

    # Receive message from the group
    async def new_message(self, event):
        print("Msg arrived in consumer, sending ot socket")
        text = event['content']
        print("new async msg to", self.channel_group_name)
        # Send message to WebSocket
        await self.send(text_data=text)