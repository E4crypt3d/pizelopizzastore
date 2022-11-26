from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Order
from channels.db import database_sync_to_async


class TrackOrder(AsyncWebsocketConsumer):
    
    def get_group_name(self):
        return Order.objects.get(user = self.user, order_id=self.order_id).order_id
    def get_order_status(self):
        return Order.objects.get(user = self.user, order_id=self.order_id).status
    
    async def connect(self):
        self.user = self.scope['user']
        if self.user.is_authenticated:
            await self.accept()
        else:
            print('closing')
            await self.close()
        self.order_id = self.scope['url_route']['kwargs']['order_id']
        self.order_group_name = await database_sync_to_async(self.get_group_name)()
        
        await self.channel_layer.group_add(self.order_group_name, self.channel_name)
        self.status = await database_sync_to_async(self.get_order_status)()
        await self.send(text_data=self.status)
        
    async def order_update(self, event):
        await self.send(text_data=event['value'])
        
    
    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.order_group_name, self.channel_name)