from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.models import User, auth
from django.contrib.auth import authenticate, login
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
        
        user = auth.authenticate(request, username=username, password=password)

        if user is not None and user.is_active and user.is_superuser == False:
            auth.login(request, user)
            return redirect('index')
        else:
            messages.info(request, "Invalid Credentials")
            return redirect('login')
    else:
        return render(request, 'user/login.html')

def buynow(request):
    id=request.GET['pid']
    price = Product.objects.get(id=id).price
    addresses = Address.objects.filter(user=request.user)
    cart=Cart.objects.create(user=request.user,product_id=id,quantity=1)
    return render(request,'user/checkout.html',{'price':price,'addresses':addresses})
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
    print(id)
    cart = Cart.objects.get(id=id)
    cart.delete()
    return redirect('cart')

def view_product(request):
    id = request.GET['id']
    product = Product.objects.get(id=id)
    print(product)
    prdct = Product.objects.filter(id=id)
    print(prdct)
    images = Images.objects.filter(product=prdct[0].id)
    print(images)
    return render(request, 'user/view_product.html', {'product': product, 'images':images})

def razorpay(request):
    cart = Cart.objects.filter(user=request.user)
    subtotal = 0
    for i in range(len(cart)):
        x = cart[i].product.price*cart[i].quantity
        subtotal = subtotal+x
    shipping = 0
    total = subtotal+shipping
    return JsonResponse({
                         'total': total,})
            
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
    print(user)
    print(user.accounts.phone)
    print(user.username)
    print(user.password)
    if Accounts.objects.filter(otp=otp).exists():
        # user = auth.authenticate(
        #     request, username=user.username)
        print("user=",user)
        auth.login(request, user)
        return redirect('index')
    else:
        messages.info(request, "Invalid OTP")
        return render(request, 'user/otplogin.html',{'user':user})


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
    
    if request.method == 'POST' :
        if 'address_id' in request.POST:
            
            address_id = request.POST['address_id']
            address = Address.objects.get(id=address_id)
            cart = Cart.objects.filter(user=request.user)
            subtotal = 0
            for i in range(len(cart)):
                x = cart[i].product.price*cart[i].quantity
                subtotal = subtotal+x
            shipping = 0
            total = subtotal+shipping
            return render(request, 'user/payment.html', {'subtotal': subtotal, 'total': total, 'addresses': address})
        else:
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
    # elif request.method == 'POST' and 'address_id' in request.POST:
    #     address_id = request.POST['address_id']
    #     address = Address.objects.get(id=address_id)
    #     return render(request, 'user/payment.html', {'address': address})
    else:
        user = request.user
        cart = Cart.objects.filter(user=user)
        addresses = Address.objects.filter(user=user)
        print(addresses)
        print(cart)
        subtotal = 0
        for i in range(len(cart)):
            x = cart[i].product.price*cart[i].quantity
            subtotal = subtotal+x
        shipping = 0
        total = subtotal+shipping
        return render(request, 'user/checkout.html', {'subtotal': subtotal, 'total': total, 'addresses': addresses})


def payment(request):
    if request.method == 'POST':
        user = request.user
        method = request.POST['payment']
        amount = request.POST['amount']
        cart = Cart.objects.filter(user=user)
        # razorpay_payment_id = request.POST['razorpay_payment_id']
        # print(razorpay_payment_id)
        address = request.POST['address']
        print("address",address)
        address = Address.objects.get(id=address)
        prdct = Product.objects.all()
        # print(cart[0].quantity)
        
        
        # crt = Cart.objects.get(user=user)
        # print(cart)
        subtotal = 0
        for i in range(len(cart)):
            x = cart[i].product.price*cart[i].quantity
            # prdct.quantity=prdct.quantity-cart[i].quantity
            subtotal = subtotal+x
        shipping = 0
        total = subtotal + shipping
        crt = Cart.objects.filter(user=user)
       
        print(method)
        order = Order.objects.create(
            user=user, address=address, amount=total, method=method)
        order.save()

        for i in range(len(cart)):
            oldcart = OldCart.objects.create(
                user=user, quantity=crt[i].quantity, product=crt[i].product, order=order)
            oldcart.save()

        cart.delete()
        success = True
        product = Product.objects.all()
        categories = Category.objects.all()
        print("==",categories)
        payMode=request.POST['payment']
        if payMode=='Razorpay':
            print(payMode)
            return JsonResponse({'status' : "Your Order has been placed successfully"})
        
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
    order = Order.objects.filter(user=request.user).order_by('-id')
    cart = Cart.objects.filter(user=request.user)
    oldcart = OldCart.objects.filter(user=request.user)
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

def profile(request):
    user = request.user
    address = Address.objects.filter(user=user)
    return render(request, 'user/profile.html', {'user': user, 'address': address})

def deleteaddress(request):
    id=request.GET['id']
    address = Address.objects.get(id=id)
    address.delete()
    return redirect('profile')

@login_required(login_url='login')
def addtocart(request):
    pid = request.GET['pid']
    # quantity = request.POST['quantity']
    # print(quantity)
    product = Product.objects.get(id=pid)
    
    uid = request.user
    print("pid =", pid)
    print("uid =", uid)
    if Cart.objects.filter(product=pid, user=uid).exists():
        cart = Cart.objects.get(product=pid, user=uid)
        cart.quantity = cart.quantity+1
        cart.save()
        return redirect('cart')
    else:
        cart = Cart.objects.create(product=product, user=uid)
        cart = Cart.objects.filter(user=uid)
        return redirect('cart')


def cancelorder(request):
    user = request.user
    id = request.GET['id']
    Order.objects.filter(id=id).update(status='Cancelled', cancel=True)
    return JsonResponse({'status': True})
    # return redirect('myorder')


def logout(request):
    # user=request.user
    auth.logout(request)
    return redirect('index')
