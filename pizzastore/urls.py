from django.urls import path
from . import views

urlpatterns = [
    path('',views.Home.as_view(), name='home'),
    path('checkout',views.CheckoutCart.as_view(), name='checkout'),
    path('login-signup',views.LoginUser.as_view(), name='log-sign'),
    path('signup',views.SignUpUser.as_view(), name='signup'),
    path('logout',views.LogoutUser.as_view(), name='logout'),
    path('order-placed',views.OrderPlaced.as_view(), name='orderplaced'),
    
    path('removeitem/<int:pk>',views.delete_cart_item, name='deleteitem'),
    path('add-item',views.add_to_cart, name='add-cart'),
    path('clearcart',views.clear_cart, name='clearcart'),
    path('incre-quan',views.add_remove_cart, name='add'),
    path('decre-quan',views.add_remove_cart, name='remove'),
    path('order',views.place_order, name='order'),
    path('search',views.pizza_search, name='search'),
    path('tracking/<str:order_id>',views.track_order, name='track'),
    path('contact',views.contactus, name='contact'),
    path('about',views.aboutus, name='about'),
    path('payment-init',views.payment_secret, name='payment-secret'),
    path('online/payment',views.online_payment, name='online-payment'),
    path('verify/payment',views.verify_payment, name='verify-payment'),
] 