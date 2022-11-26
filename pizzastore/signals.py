from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Order
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

@receiver(pre_save, sender=Order)
def order_update(sender,instance, **kwargs):
    channel_layer = get_channel_layer()
    
    async_to_sync(channel_layer.group_send)(instance.order_id, {
        
        'type':'order.update',
        'value':instance.status
    })