from django.contrib import admin
from .models import Pizza, Cart, Order, ShippingDetail
# Register your models here.

admin.AdminSite.index_title = "Pizelo"
admin.AdminSite.site_title = "Management"
admin.AdminSite.site_header = "Pizelo Management"

@admin.register(Pizza)
class PizzaAdmin(admin.ModelAdmin):
    list_display = ['id','pizza_name','category','price','added_on']
    list_display_links = ['id','pizza_name','category','price','added_on']


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id','user','product','total_price']
    list_display_links = ['id','user','product','total_price']
    
    


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id','user','order_item','order_on','status', 'order_id','delivered']
    list_display_links = ['id','user','order_item','order_on','status', 'order_id','delivered']
    list_filter = ['delivered']
    readonly_fields = ['order_id','order_on','delivered','user','order_item','address','order_quantity']
    search_fields = ['order_item__pizza_name']
    
    
@admin.register(ShippingDetail)
class ShippingDetail(admin.ModelAdmin):
    list_display = ['id','user','address','email','city', 'name']
    list_display_links = ['id','user','address','email','city', 'name']