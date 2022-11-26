from django.db import models
import string
import datetime
import random
from django.contrib.auth.models import User

# Create your models here.
class Pizza(models.Model):
    pizza_name = models.CharField(max_length=255)
    category = models.CharField(max_length=128)
    price = models.PositiveIntegerField()
    compare_price = models.PositiveIntegerField(null=True, blank=True, default=None)
    image = models.ImageField(upload_to='pizzas')
    ingredients = models.CharField(max_length=400)
    added_on = models.DateField(auto_now=True)
    baking_time = models.PositiveSmallIntegerField(default=1)
    
    
    def __str__(self):
        return self.pizza_name
    
    
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name = 'cart_user')
    product = models.ForeignKey('Pizza', on_delete=models.CASCADE, related_name='product')
    quantity = models.PositiveIntegerField(default=1)
    
    TAX_AMOUNT = 750
    
    @property
    def total_price(self):
        return self.product.price * self.quantity
    
    def __str__(self):
        return self.user.username



class Order(models.Model):
    status_choices = [
        ('Order Received', 'Order Received'),
        ('Baking', 'Baking'),
        ('Baked', 'Baked'),
        ('On The Way', 'On The Way'),
        ('Delivered', 'Delivered')]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='order_user')
    order_item = models.ForeignKey('Pizza', on_delete=models.CASCADE, related_name='order_item')
    order_id = models.CharField(max_length=12, blank=True)
    order_on = models.DateTimeField(auto_now=True)
    order_quantity=models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=128, choices=status_choices, default='Order Received')
    address = models.CharField(max_length=350, default="")
    delivered = models.BooleanField(default=False)
    online_pay = models.BooleanField(default=False)
    
    
    def __str__(self):
        return self.order_id
        
    
    def delivery_time(self):
        time = self.order_on
        estimated_time = time + datetime.timedelta(hours=5, minutes=self.order_item.baking_time)
        return estimated_time
    
    @property
    def order_total(self):
        return Cart.TAX_AMOUNT + (self.order_item.price * self.order_quantity)

    
    def save(self, force_insert=None, using=None):
        if self.status == "Delivered":
            self.delivered = True
        if not self.order_id:
            letters = string.ascii_uppercase
            digits = string.digits
            self.order_id = ''.join(random.choice(letters+digits) for i in range(12))
        return super().save()
    
    
    
class ShippingDetail(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='shippinguser')
    address = models.CharField(max_length=154)
    city = models.CharField(max_length=128)
    email = models.EmailField()
    name = models.CharField(max_length=160)
    
    
    def __str__(self):
        return self.name