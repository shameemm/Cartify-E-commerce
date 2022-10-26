from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.models import User, auth
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from accounts.models import Accounts
from admins.models import *
import uuid
from .models import *
from django.db.models import Sum
from .mixins import MessageHandler
import random
from django.http import FileResponse
from fpdf import FPDF
from copy import deepcopy
import io
from django.http import FileResponse
from reportlab.pdfgen import canvas
from django.template.loader import get_template
from xhtml2pdf import pisa
from django import template
from guest_user.decorators import allow_guest_user
from guest_user.models import Guest
register = template.Library()

@allow_guest_user()
def guestsignup(request):
    print(request.user.id)
    id = request.user.id
    if request.method == 'POST':
        if request.method == 'POST' and 'otp' not in request.POST:
            first_name = request.POST['first_name']
            last_name = request.POST['last_name']
            phone = request.POST['phone']
            email = request.POST['email']
            username = request.POST['username']
            password = request.POST['password']
        
            if User.objects.filter(username=username).exists():
                # messages.info(request, 'Username Taken')
                # return redirect('guestsignup')
                userexist = "Username Taken"
                return JsonResponse({'userexist': userexist})
            elif User.objects.filter(email=email).exists():
                messages.info(request, 'Email Taken')
                return redirect('guestsignup')
            else:
                # otp=random.randint(100000,999999)
                # otp = otpgenerate()
                otp = 968542
                # print(username)
                print(otp)
                message_handler = MessageHandler(phone, otp).sent_otp_on_phone()
                return render(request, "user/otpgsignup.html",{ 'first_name': first_name, 'last_name': last_name, 'phone': phone, 'email': email, 'username': username, 'password': password, 'otp': otp})
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
                user = User.objects.create_user(id=id,first_name=first_name, last_name=last_name,  username=username, email=email, password=password)
                user.save_base()
                user_id = User.objects.get(username=username)
                account = Accounts.objects.create(user=user_id, phone=phone)
                account.save()
                guest = Guest.objects.get(user_id=id)
                guest.delete()
                print('user created')
                return render(request,'user/login.html')
            else:
                messages.info(request, "Invalid Otp")
                return render(request, 'user/otpgsignup.html')
    else:
        return render(request, 'user/guestsignup.html')
        
    

@register.simple_tag()
def multiply(qty, unit_price, *args, **kwargs):
    # you would need to do any localization of the result here
    return qty * unit_price
# Create your views here.


def login(request):
    if request.user:
        print(request.user.id)
        cart = Cart.objects.get(user=request.user)
        print(cart.product)
        if request.user.is_superuser:
            return redirect('adminhome')
        if request.method == 'POST':
            # username = request.POST['username']
            # password = request.POST['password']
            # user = auth.authenticate(username=username, password=password)
            # if user is not None:
            #     auth.login(request, user)
            #     return redirect('index')
            # else:
            #     messages.info(request, 'invalid credentials')
            #     return redirect('login')
            username = request.POST['username']
            password = request.POST['password']
            
            user = auth.authenticate(request, username=username, password=password)
            if user is not None and user.is_active and user.is_superuser == False:
                auth.login(request, user)
                pid = cart.product_id
                uid = user.id
                if Cart.objects.filter(product=pid, user=uid).exists():
                    cart = Cart.objects.get(product=pid, user=user)
                    cart.quantity = cart.quantity+1
                    cart.save()
                    return redirect('index')
                else:
                    cart = Cart.objects.filter(user=request.user).update(user=user)
                    print(user)
                    print("req",request.user)
                    return redirect('index')
            else:
                messages.info(request, "Invalid Credentials")
            return redirect('login')
            cart = Cart.objects.filter(user=request.user).update(user=user)
            print(user)
            print("req",request.user)
        
    if request.user.is_authenticated and request.user.is_superuser == False and request.user.first_name != '':
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
    
    print(uuid.uuid4())
    request.session['cart'] =str(random.randint(100000, 999999))
    
    product = Product.objects.all()
    categories = Category.objects.all()
    
    if request.user.is_authenticated and request.user.is_superuser == False:
        print(request.user.is_authenticated)
        user = request.user
        print('user=', user)
        return render(request, 'user/home.html', {'user': user, 'products': product, 'categories': categories})
    else:
        return render(request, 'user/home.html', {'products': product, 'categories': categories})

def invoice( request):
    id = request.GET['id']
    order = Order.objects.filter(id=id)
    user = request.user
    address=order[0].address
    cart = OldCart.objects.filter(order_id=id)
    print(address)
    print(cart)
    

    template_path = 'user/invoice.html'

    context = {'order': order, 'address':address, 'user': user, 'cart': cart}

    response = HttpResponse(content_type='application/pdf')

    response['Content-Disposition'] = 'filename="invoice.pdf"'

    template = get_template(template_path)

    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(
       html, dest=response)
    # if error then show some funy view
    if pisa_status.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

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
    print(request.session['cart'])
    id = request.GET['id']
    print(id)
    product = Product.objects.get(id=id)
    print(product)
    prdct = Product.objects.filter(id=id)
    print(prdct)
    images = Images.objects.filter(product=prdct[0].id)
    offers = Offers.objects.all()
    for offer in offers:
        if offer.product == prdct[0]:
            # print("offer=",offer.name)
            for ofr in offers:
                # print("offer=",offer.name)
                if ofr.category == product.category:
                    print("ofr=",ofr.name)
                    if ofr.offer<offer.offer:
                        print("offer",offer.offer)
                        return render(request, 'user/view_product.html',{'product': product, 'images': images, 'offer': offer})
                    else:
                        return render(request, 'user/view_product.html',{'product': product, 'images': images, 'offer':ofr})
                # else:
                    
        else: 
            for ofr in offers:
                # print("offer=",offer.name)
                if ofr.category == product.category:
                    print("elseofr=",ofr.name)
                    return render(request, 'user/view_product.html',{'product': product, 'images': images, 'offer':ofr})
                        
                        
                    
            # print(offer)
            # return render(request, 'user/product.html', {'product': product, 'images': images, 'offer': offer})
    # for offer in offers:
        
    #     if offer.product == product and offer.category == product.category:
    #         print("offer = ",offer.name)
    #         return render(request, 'user/view_product.html', {'product': product, 'images': images, 'offer': offer})
    #     elif offer.category == product.category:
    #         print("offer = ",offer.name)
    #         return render(request, 'user/view_product.html', {'product': product, 'images': images, 'offer': offer})
    
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
    
    crt = Cart.objects.filter(user=request.user)
    Cart.objects.filter(id=id).update(quantity=qty)
    # return redirect('cart')
    subtotal = 0
    for i in range(len(crt)):
        if crt[i].cancel != True:
            if crt[i].price_with_offer !=0:
                x = crt[i].price_with_offer*crt[i].quantity
                subtotal = subtotal+x
            else:
                x = crt[i].product.price*crt[i].quantity
                subtotal = subtotal+x
    shipping = 0
    total = subtotal + shipping
    return JsonResponse({'data': qty,'total':total,'subtotal':subtotal})

def up(request):
    id = request.GET['id']
    crt = Cart.objects.filter(user=request.user)
    cart = Cart.objects.get(id=id)
    qty = cart.quantity+1
    print(qty)
    Cart.objects.filter(id=id).update(quantity=qty)
    subtotal = 0
    for i in range(len(crt)):
        if crt[i].cancel != True:
            if crt[i].price_with_offer !=0:
                x = crt[i].price_with_offer*crt[i].quantity
                subtotal = subtotal+x
            else:
                x = crt[i].product.price*crt[i].quantity
                subtotal = subtotal+x
    shipping = 0
    total = subtotal + shipping
    # return redirect('cart')
    return JsonResponse({'data': qty,'total':total,'subtotal':subtotal})


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
        offers = Offers.objects.all()
        for i in range(len(cart)):
            if cart[i].quantity < 1:
                cart[i].delete()
        if len(cart) == 0:
            empty = "Cart is Empty"
            return render(request, 'user/cart.html', {'empty': empty, 'offers': offers})
        else:
            subtotal = 0
            for i in range(len(cart)):
                if cart[i].cancel != True:
                    if cart[i].price_with_offer !=0:
                        x = cart[i].price_with_offer*cart[i].quantity
                        subtotal = subtotal+x
                    else:
                        x = cart[i].product.price*cart[i].quantity
                        subtotal = subtotal+x
            shipping = 0
            total = subtotal + shipping
            return render(request, 'user/cart.html', {'cart': cart, 'subtotal': subtotal, 'total': total, 'offers': offers})
    else:
        return redirect('login')

@login_required(login_url='login')
def addaddress(request):
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
        return redirect('checkout')
    else:
        return render(request, 'user/addaddress.html')
    
@login_required(login_url='login')
def checkout(request):
    print('checkput')
    if request.method == 'POST' and 'address_id' in request.POST :
        address_id = request.POST['address_id']
        address = Address.objects.get(id=address_id)
        cart = Cart.objects.filter(user=request.user)
        subtotal = 0
        for i in range(len(cart)):
            if cart[i].cancel != True:
                if cart[i].price_with_offer !=0:
                    x = cart[i].price_with_offer*cart[i].quantity
                    subtotal = subtotal+x
                else:
                    x = cart[i].product.price*cart[i].quantity
                    subtotal = subtotal+x
        shipping = 0
        total = subtotal+shipping
        return render(request, 'user/payment.html', {'subtotal': subtotal, 'total': total, 'addresses': address,'cart':cart})
    elif request.method == 'POST' and 'code' in request.POST:
        user = request.user
        method = request.POST['payment']
        amount = request.POST['amount']
        address = request.POST['address']
        cart = Cart.objects.filter(user=user)
        print("address",address)
        total = float(request.POST['amount'])
        code = request.POST['code']
        print(code)
        subtotal = 0
        for i in range(len(cart)):
            if cart[i].cancel != True:
                if cart[i].price_with_offer !=0:
                    x = cart[i].price_with_offer*cart[i].quantity
                    subtotal = subtotal+x
                else:
                    x = cart[i].product.price*cart[i].quantity
                    subtotal = subtotal+x
        shipping = 0
        message=False
        coupon = Coupon.objects.get(code=code)
        if total>coupon.min_amount:
            total = total-coupon.discount
        else:
            message = "Minimum Amount is not reached"    
        print(message)
        print(total)
        return render(request, 'user/payment.html', { 'subtotal':subtotal,'total': total,'message':message, 'addresses': address,'cart':cart, 'code':code, 'offer':coupon})
    else:
        print('else===')
        user = request.user
        cart = Cart.objects.filter(user=user)
        addresses = Address.objects.filter(user=user)
        print(addresses)
        print(cart)
        subtotal = 0
        for i in range(len(cart)):
            if cart[i].cancel != True:
                if cart[i].price_with_offer !=0:
                    x = cart[i].price_with_offer*cart[i].quantity
                    subtotal = subtotal+x
                else:
                    x = cart[i].product.price*cart[i].quantity
                    subtotal = subtotal+x
        total = subtotal
        # return HttpResponse('else')
        return render(request, 'user/checkout.html', {'subtotal': subtotal, 'total': total, 'addresses': addresses})


def payment(request):
    if request.method == 'POST':
        user = request.user
        method = request.POST['payment']
        amount = request.POST['amount']
        print(amount)
        cart = Cart.objects.filter(user=user)
        address = request.POST['address']
        print("address",address)
        address = Address.objects.get(id=address)
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
            user=user, address=address, amount=amount, method=method)
        order.save()
        for i in range(len(cart)):
            oldcart = OldCart.objects.create(
                user=user, quantity=crt[i].quantity, product=crt[i].product, order=order)
            oldcart.save()
        cart.delete()
        prdcts=OldCart.objects.filter(order=order)
        for i in range(len(prdcts)-1):
            p=Product.objects.filter(id=prdcts[i].product.id)
            # # print("qty",p[i].quantity)
            # print("cartqty",prdcts[i].quantity)
            # print("pqty",p[i].quantity-prdcts[i].quantity)
            # print("pid",prdcts[i].product.id)
            Product.objects.filter(id=prdcts[i].product.id).update(quantity=p[i].quantity-prdcts[i].quantity)
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
    
# @login_required(login_url='login')
# def applycoupon(request):
#     code = request.POST['code']
#     print(code)
#     offer = Offers.objects.filter(code=code)
#     print(offer[0].amount)
#     amount = offer[0].amount
#     return redirect('payment')

@login_required(login_url='login')
def returnorder(request):
    print(request.GET['id'])
    id=int(request.GET['id'])
    print(id)
    order = Order.objects.get(id=id)
    user = request.user
    status = 'Return Requested'
    reason = request.POST['reason']
    order = Order.objects.filter(id=id).update(status=status, reason=reason)
    
    print(order)
    
    return redirect('myorder')

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

@allow_guest_user
@login_required(login_url='login')
def addtocart(request):
    pid = request.GET['pid']
    # quantity = request.POST['quantity']
    # print(quantity)
    product = Product.objects.get(id=pid)
    offers = Offers.objects.all()
    
    uid = request.user
    print("pid =", pid)
    print("uid =", uid)
    if Cart.objects.filter(product=pid, user=uid).exists():
        cart = Cart.objects.get(product=pid, user=uid)
        cart.quantity = cart.quantity+1
        cart.save()
        return redirect('cart')
    else:
        for offer in offers:
            if offer.product == product:
                price = 0
                offamount = product.price * offer.offer / 100
                if offamount > offer.max_value:
                    price = product.price - offer.max_value
                else:
                    price = product.price - offamount
                print(price)
                cart = Cart.objects.create(
                    user=uid, product=product, quantity=1, price_with_offer=price)
                cart.save()
                return redirect('cart')
        
        cart = Cart.objects.create(product=product, user=uid)
        cart = Cart.objects.filter(user=uid)
        return redirect('cart')


def cancelorder(request):
    user = request.user
    id = request.GET['id']
    Order.objects.filter(id=id).update(status='Cancelled', cancel=True)
    return JsonResponse({'status': True})
    # return redirect('myorder')

def category(request):
    id=request.GET['id']
    product=Product.objects.filter(category=id)
    categoty=Category.objects.all()
    return render(request,'user/home.html',{'products':product,'categories':categoty})

def logout(request):
    # user=request.user
    auth.logout(request)
    return redirect('index')
