from django.shortcuts import render, redirect, HttpResponse
from django.http import JsonResponse
from django.db.models import Sum, F
from django.views.generic import ListView, CreateView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Pizza, Cart, Order, ShippingDetail
from django.contrib.auth.decorators import login_required
from .forms import SignUpForm, LoginForm
from django.urls import reverse
from django.core.mail import get_connection, EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import stripe
from .mail_task import payment_mail
from django.contrib.auth.models import Group


# This is your test secret API key.
stripe.api_key = settings.STRIPE_TOKEN

# Create your views here.
class Home(ListView):
    template_name: str = 'pizzastore/index.html'
    model = Pizza
    context_object_name = 'pizzas'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['carts'] = Cart.objects.prefetch_related('product','user').filter(user=self.request.user)
            context['cart_totals'] = context['carts'].aggregate(total_products=Sum('quantity'))
            total_price = 0
            for i in context['carts']:
                total_price += i.total_price
            context['cart_totals']['total_price'] = total_price
        return context

class CheckoutCart(LoginRequiredMixin,ListView):
    template_name = 'pizzastore/checkout.html'
    context_object_name = 'carts'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cart_totals'] = context['carts'].aggregate(total_products=Sum('quantity'))
        total_price = 0
        for i in context['carts']:
            total_price += i.total_price
        context['cart_totals']['total_price'] = total_price
        context['tax'] = Cart.TAX_AMOUNT
        if context['cart_totals']['total_price'] == None:
            context['cart_totals']['total_price'] = 0
        return context

    
    def get_queryset(self):
        return Cart.objects.prefetch_related('product','user').filter(user=self.request.user)

class OrderPlaced(LoginRequiredMixin, ListView):
    template_name = 'pizzastore/order_placed.html'
    context_object_name = 'orders'
    
    def get_queryset(self):
        return Order.objects.prefetch_related('order_item','user').filter(user=self.request.user, delivered=False)


class LoginUser(LoginView):
    template_name = 'pizzastore/login_signup.html'
    next_page = 'home'
    redirect_authenticated_user = True
    authentication_form = LoginForm
    
    def get_template_names(self):
        if self.request.htmx:
            return ['pizzastore/partials/login.html']
        else:
            return [self.template_name]

class LogoutUser(LogoutView):
    next_page = 'home'

class SignUpUser(CreateView):
    form_class = SignUpForm
    template_name = 'pizzastore/partials/signup.html'
    
    def get_success_url(self):
        return reverse('log-sign')  
    
    def form_valid(self, form):
        self.object = form.save()
        group = Group.objects.get(name='customer')
        self.object.groups.add(group)
        return super().form_valid(form)
    
    


@login_required
def delete_cart_item(request, pk):
    if request.method == 'POST':
        Cart.objects.get(pk=pk).delete()
        cart = Cart.objects.prefetch_related('product','user').filter(user=request.user)
        cart_totals = cart.aggregate(total_products=Sum('quantity'))
        total_price = 0
        for i in cart:
            total_price += i.total_price
        context = {'carts':cart, 'cart_totals':cart_totals}
        context['cart_totals']['total_price'] = total_price
        if request.POST.get('sidecart','false') == 'true':
            context['tax'] = Cart.TAX_AMOUNT
            return render(request, 'pizzastore/partials/sidecart.html', context)
        return render(request, 'pizzastore/partials/cart.html', context)

@login_required()
def add_to_cart(request):
    if request.method == 'POST' and request.user.is_authenticated:
        productid = Pizza.objects.get(id=request.POST['product'])
        cart_check, created = Cart.objects.get_or_create(product=productid, user=request.user)
        if not created:
            cart_check.quantity+=1
            cart_check.save()
        cart = Cart.objects.prefetch_related('product','user').filter(user=request.user)
        cart_totals = cart.aggregate(total_products=Sum('quantity'))
        total_price = 0
        for i in cart:
            total_price += i.total_price
        context = {'carts':cart, 'cart_totals':cart_totals}
        context['cart_totals']['total_price'] = total_price
        return render(request, 'pizzastore/partials/cart.html', context)

@login_required
def clear_cart(request):
    if request.method == 'POST':
        Cart.objects.filter(user=request.user).delete()
        return render(request, 'pizzastore/partials/cart.html')

@login_required
def add_remove_cart(request):
    if request.method == 'POST':
        addid = request.POST.get('item', None)
        action = request.POST.get('action', None)
        cart = Cart.objects.prefetch_related('product','user').filter(user=request.user)
        
        if action == 'add':
            cart.filter(pk=addid).update(quantity = F('quantity')+1)
        elif action == 'remove':
            if cart.get(pk=addid).quantity == 1:
                cart.filter(pk=addid).delete()
            else:
                cart.filter(pk=addid).update(quantity = F('quantity')-1)
        cart_totals = cart.aggregate(total_products=Sum('quantity'))
        
        total_price = 0
        for i in cart:
            total_price += i.total_price
        context = {'carts':cart, 'cart_totals':cart_totals}
        context['cart_totals']['total_price'] = total_price
        return render(request, 'pizzastore/partials/cart.html',context)

@login_required  
def place_order(request):
    if request.method == 'POST':
        payment_method = request.POST['paymethod']
        user = request.user
        address = request.POST['address']
        city = request.POST['city']
        email = request.POST['email']
        rememberme = request.POST.get('rememberme','off')
        if rememberme == 'on':
            ShippingDetail.objects.get_or_create(user=request.user,address=address, city=city,name=request.POST['name'], email=email)
        elif rememberme == 'off':
            ShippingDetail.objects.get(user=request.user).delete()
        if payment_method == 'Pay Online':
            request.session['address'] = address
            request.session['email'] = email
            return redirect(reverse('online-payment'))
        carts = Cart.objects.prefetch_related('product','user').filter(user=user)
        for cart in carts:
            Order.objects.create(user=user, order_item=cart.product,order_quantity=cart.quantity, address=address)
        carts.delete()
        return redirect(reverse('orderplaced'))
    
def pizza_search(request):
    search = request.GET.get('search', '')
    if len(search) > 3:
        pizza_search = Pizza.objects.filter(pizza_name__icontains=search).order_by('-id')
        return render(request, 'pizzastore/partials/search_results.html',{'pizza_search':pizza_search})

def track_order(request, order_id):
    try:
        order = Order.objects.prefetch_related('order_item','user').get(order_id=order_id, delivered=False, user=request.user)
        context = {'order':order}
        return render(request, 'pizzastore/order_tracking.html', context)
    except Exception:
        return redirect(reverse('orderplaced'))
    
def contactus(request):
    if request.method == "POST":
        name = request.POST.get('name',None)
        email = request.POST.get('email',None)
        message = request.POST.get('message',None)
        if name and email and message != None and len(name) >=2:
            success_msg = 'Thanks for contacting us we will get back to you soon'
            customermsg = (
            'Pizelo Support',
            success_msg,settings.DEFAULT_FROM_EMAIL,[email],)
            adminmsg = (
            'Pizelo Contact',
            f'{name} @{email} : {message}',settings.DEFAULT_FROM_EMAIL,[settings.DEFAULT_FROM_EMAIL],)
            emails = (adminmsg, customermsg)
            connection = get_connection()
            connection.open()
            for email in emails:
                if email[0] == 'Pizelo Contact':
                    context = {'title':email[1]}
                else:
                    context = {'title':success_msg}
                html_message = render_to_string('email.html', context)
                msg = EmailMultiAlternatives(email[0],email[1],email[2],email[3])
                msg.attach_alternative(html_message, 'text/html')
                msg.send()
            connection.close()
            return HttpResponse('<p id="alert" style="color: #16ff16;transition: opacity 5s ease-in-out;opacity: 1;">Your form has been submitted</p>')
        else:
            return HttpResponse('<p id="alert" class="text-red-600 successfully-saved" style="color: #f95050;">Error occured Please check your form</p>')
    return render(request, 'pizzastore/contact.html')


def aboutus(request):
    return render(request, 'pizzastore/about.html')


@login_required
def payment_secret(request):
    try:
        user = request.user
        carts = Cart.objects.filter(user=user)
        amount = sum([c.total_price for c in carts]) + Cart.TAX_AMOUNT

        # Create a PaymentIntent with the order amount and currency
        payment = stripe.PaymentIntent.create(
            amount=amount,
            currency='usd',
            automatic_payment_methods={
                'enabled': True,
            },
        )
        return JsonResponse({
            'clientSecret': payment.client_secret
        })
    except Exception as e:
        return JsonResponse({'error':str(e)})

@login_required
def online_payment(request):
    if Cart.objects.filter(user=request.user).exists():
        return render(request, 'pizzastore/payment.html')
    else:
        return redirect(reverse('checkout'))

@login_required
def verify_payment(request):
    user = request.user
    address = request.session['address']
    email = request.session['email']
    payment_intent = request.GET['payment_intent']
    payment = stripe.PaymentIntent.retrieve(payment_intent)
    if payment['status'] == 'succeeded':
        carts = Cart.objects.prefetch_related('product','user').filter(user=user)
        amount = sum([c.total_price for c in carts]) + Cart.TAX_AMOUNT
        if payment['amount_received'] == amount:
            orders = []
            orders_total = 0
            for cart in carts:
                order = Order.objects.create(user=user,online_pay=True, order_item=cart.product,order_quantity=cart.quantity, address=address)
                orders.append(order)
                orders_total+=order.order_total
            carts.delete()
            email_title = "Thanks for your Purchase"
            track_url =  "{0}://{1}".format(request.scheme, request.get_host())
            html_message = render_to_string('email.html', {'orders':orders, 'total':orders_total, 'title':email_title,'url':track_url})
            plain_message = strip_tags(html_message)
            payment_mail.delay("Pizelo Order Puchased",plain_message,email,html_message)
            return redirect(reverse('orderplaced'))
        else:
            return redirect(reverse('checkout'))
    else:
        return redirect(reverse('home'))