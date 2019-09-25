from channels.generic.websocket import AsyncJsonWebsocketConsumer


class NotificationConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if self.user.is_authenticated:
            await self.channel_layer.group_add(
                self.user.id,
                self.channel_name,
            )
            await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            self.user.id,
            self.channel_name,
        )
        self.disconnect()

    async def send_notification(self, text_data=None, bytes_data=None, **kwargs):
        # Send message to WebSocket

        self.send_json(content=text_data)
