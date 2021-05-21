from asgiref.sync import async_to_sync
from channels.consumer import SyncConsumer
import json


class RunMessageConsumer(SyncConsumer):

    def websocket_connect(self, event):
        group_name = self.scope["url_route"]["kwargs"]["run_id"]

        self.send({
            'type': 'websocket.accept',
        })

        # Join group
        print("Consumer joined group", group_name)
        async_to_sync(self.channel_layer.group_add)(
            group_name,
            self.channel_name
        )


    def websocket_disconnect(self, event):

        # Leave  group
        group_name = self.scope["url_route"]["kwargs"]["run_id"]
        async_to_sync(self.channel_layer.group_discard)(
            group_name,
            self.channel_name
        )

    def new_message(self, event):
        to_sent = {
            'type': 'websocket.send',
            'text': event['content'],
        }
        self.send(to_sent)
