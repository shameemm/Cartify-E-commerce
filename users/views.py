from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from accounts.models import Accounts
from admins.models import *
from .models import *
from django.db.models import Sum
from .mixins import MessageHandler
import random
# Create your views here.


def login(request):
    if request.user.is_authenticated and request.user.is_superuser == False:
        return redirect('index')
    if request.method == 'POST' and 'username' in request.POST and 'password' in request.POST and 'otp' not in request.POST:
        username = request.POST['username']
        password = request.POST['password']
        user = User.objects.get(username=username)
        phone = user.accounts.phone
        user = auth.authenticate(request, username=username, password=password)
        otp = random.randint(100000, 999999)
        print(otp)
        numb = Accounts.objects.filter(phone=phone).update(otp=otp)
        phone = '+91'+str(phone)
        message_handler = MessageHandler(phone, otp).sent_otp_on_phone()
        return render(request, 'user/otplogin.html', {'username': username, 'password': password})
    elif request.method == 'POST' and 'otp' in request.POST:
        otp = request.POST['otp']
        username = request.POST['username']
        print(username)
        password = request.POST['password']
        print(password)
        if Accounts.objects.filter(otp=otp).exists():
            user = auth.authenticate(
                request, username=username, password=password)
            print("user = ", user)

        if user is not None and user.is_active and user.is_superuser == False:
            auth.login(request, user)
            return redirect('index')
        else:
            messages.info(request, "Invalid Credentials")
            return redirect('login')
    else:
        return render(request, 'user/login.html')


def index(request):
    product = Product.objects.all()
    categories = Category.objects.all()
    if request.user.is_authenticated:
        print(request.user.is_authenticated)
        user = request.user
        print('user=', user)
        return render(request, 'user/home.html', {'user': user, 'products': product, 'categories': categories})
    else:
        return render(request, 'user/home.html', {'products': product, 'categories': categories})


def otpgenerate():
    otp = random.randint(100000, 999999)
    return otp


def signup(request):
    # print("GEN=",otp)
    if request.method == 'POST' and 'otp' not in request.POST:
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        phone = request.POST['phone']
        email = request.POST['email']
        username = request.POST['username']
        password = request.POST['password']
        
        if User.objects.filter(username=username).exists():
            messages.info(request, 'Username Taken')
            return redirect('signup')
        elif User.objects.filter(email=email).exists():
            messages.info(request, 'Email Taken')
            return redirect('signup')
        else:
            # otp=random.randint(100000,999999)
            # otp = otpgenerate()
            otp = 968542
            print(username)
            print(otp)

            message_handler = MessageHandler(phone, otp).sent_otp_on_phone()
            return render(request, "user/otpsignup.html",{ 'first_name': first_name, 'last_name': last_name, 'phone': phone, 'email': email, 'username': username, 'password': password, 'otp': otp})
    elif request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        phone = request.POST['phone']
        email = request.POST['email']
        username = request.POST['username']
        password = request.POST['password']
        print("username=", username)
        print(password)
        otp = 968542
        otp1 =int( request.POST['otp'])
        # print("otp1=",otp1)
        if otp==otp1:
            user = User.objects.create_user(
                first_name=first_name, last_name=last_name,  username=username, email=email, password=password)
            user.save()
            user_id = User.objects.get(username=username)
            account = Accounts.objects.create(user=user_id, phone=phone)
            account.save()
            print('user created')
            return render(request,'user/login.html')
        else:
            messages.info(request, "Invalid Otp")
            return render(request, 'user/otpsignup.html')
    else:
        return render(request, 'user/signup.html')

def removecart(request):
    id=request.GET['id']
    cart = Cart.objects.get(id=id)
    cart.delete()
    return redirect('cart')
def view_product(request):
    id = request.GET['id']
    product = Product.objects.get(id=id)
    return render(request, 'user/view_product.html', {'product': product})


def minus(request):
    id = request.GET['id']
    cart = Cart.objects.get(id=id)
    qty = cart.quantity-1
    print(qty)
    Cart.objects.filter(id=id).update(quantity=qty)
    return redirect('cart')


def up(request):
    id = request.GET['id']
    cart = Cart.objects.get(id=id)
    qty = cart.quantity+1
    print(qty)
    Cart.objects.filter(id=id).update(quantity=qty)
    return redirect('cart')


def getotp(request):
    phone = request.POST['phone']
    if not Accounts.objects.filter(phone=phone).exists():
        messages.info(request, "Phone Number Not Registered")
        return redirect('login')
    else:
        number = Accounts.objects.get(phone=phone)
        num = Accounts.objects.filter(phone=phone)
        print('1', number.phone)
        user = User.objects.get(id=number.user_id)
        otp = random.randint(100000, 999999)
        numb = Accounts.objects.filter(phone=phone).update(otp=otp)
        print(otp)

        message_handler = MessageHandler(phone, otp).sent_otp_on_phone()
        return render(request, 'user/otplogin.html', {'user': user})


def otplogin(request):
    id = request.GET['id']
    otp = request.POST['otp']
    user = User.objects.get(id=id)
    print(user.accounts.phone)
    if Accounts.objects.filter(otp=otp).exists():
        user = auth.authenticate(
            request, username=user.username, password=user.password)
        auth.login(request, user)
        return redirect('index')
    else:
        messages.info(request, "Invalid OTP")
        return redirect('login')


@login_required(login_url='login')
def cart(request):
    if request.user.is_authenticated:
        user = request.user
        cart = Cart.objects.filter(user=user)

        for i in range(len(cart)):

            if cart[i].quantity < 1:
                cart[i].delete()
        if len(cart) == 0:
            empty = "Cart is Empty"
            return render(request, 'user/cart.html', {'empty': empty})
        else:
            subtotal = 0
            for i in range(len(cart)):
                if cart[i].cancel != True:
                    x = cart[i].product.price*cart[i].quantity
                    subtotal = subtotal+x
            shipping = 0
            total = subtotal + shipping
            return render(request, 'user/cart.html', {'cart': cart, 'subtotal': subtotal, 'total': total})
    else:
        return redirect('login')


@login_required(login_url='login')
def checkout(request):
    if request.method == 'POST':
        user = request.user
        name = request.POST['name']
        phone = request.POST['phone']
        address = request.POST['address']
        city = request.POST['city']
        state = request.POST['state']
        pincode = request.POST['pincode']
        address = Address.objects.create(
            name=name, phone=phone, address=address, city=city, state=state, pincode=pincode, user=user)
        address.save()
        return redirect('payment')
    else:
        user = request.user
        cart = Cart.objects.filter(user=user)
        print(cart)
        subtotal = 0
        for i in range(len(cart)):
            x = cart[i].product.price*cart[i].quantity
            subtotal = subtotal+x
        shipping = 0
        total = subtotal+shipping
        return render(request, 'user/checkout.html', {'subtotal': subtotal, 'total': total})


def payment(request):
    if request.method == 'POST':
        user = request.user
        method = request.POST['payment']
        amount = request.POST['amount']
        cart = Cart.objects.filter(user=user)
        address = Address.objects.filter(user=user)
        prdct = Product.objects.all()
        print(cart[0].quantity)
        
        
        # crt = Cart.objects.get(user=user)
        print(cart)
        subtotal = 0
        for i in range(len(cart)):
            x = cart[i].product.price*cart[i].quantity
            # prdct.quantity=prdct.quantity-cart[i].quantity
            subtotal = subtotal+x
        shipping = 0
        total = subtotal + shipping
        crt = Cart.objects.filter(user=user)
        n = len(address)
        print(method)
        order = Order.objects.create(
            user=user, address=address[n-1], amount=total, method=method)
        order.save()

        for i in range(len(cart)):
            oldcart = OldCart.objects.create(
                user=user, quantity=crt[i].quantity, product=crt[i].product, order=order)
            oldcart.save()

        cart.delete()
        success = True
        product = Product.objects.all()
        categories = Category.objects.all()
        return render(request, 'user/home.html', {'user': user, 'products': product, 'categories': categories, 'success': success})
    else:
        user = request.user
        cart = Cart.objects.filter(user=user)
        subtotal = 0
        for i in range(len(cart)):
            x = cart[i].product.price*cart[i].quantity
            subtotal = subtotal+x
        shipping = 0
        total = subtotal + shipping
        return render(request, 'user/payment.html', {'subtotal': subtotal, 'total': total, 'cart': cart})


@login_required(login_url='login')
def myorder(request):
    order = Order.objects.filter(user=request.user)
    cart = Cart.objects.filter(user=request.user)
    oldcart = OldCart.objects.filter(user=request.user)
    # print(order[0].cancel)
    # print(oldcart[1].product)
    if len(order) == 0:
        empty = "No Order Placed"
        return render(request, 'user/orders.html', {'empty': empty})
    subtotal = 0
    for i in range(len(cart)):
        x = cart[i].product.price*cart[i].quantity
        subtotal = subtotal+x
    shipping = 0
    total = subtotal + shipping
    return render(request, 'user/orders.html', {'orders': order, 'cart': oldcart, 'total': total})


@login_required(login_url='login')
def addtocart(request):
    pid = request.GET['pid']
    quantity = request.POST['quantity']
    print(quantity)
    product = Product.objects.get(id=pid)
    
    uid = request.user
    print("pid =", pid)
    print("uid =", uid)
    if Cart.objects.filter(product=pid, user=uid).exists():
        cart = Cart.objects.get(product=pid, user=uid)
        cart.quantity = quantity
        cart.save()
        return redirect('cart')
    else:
        cart = Cart.objects.create(product=product, user=uid, quantity=quantity)
        cart = Cart.objects.filter(user=uid)
        return redirect('cart')


def cancelorder(request):
    user = request.user
    id = request.GET['id']
    Order.objects.filter(id=id).update(status='Cancelled', cancel=True)

    return redirect('myorder')


def logout(request):
    # user=request.user
    auth.logout(request)
    return redirect('index')
