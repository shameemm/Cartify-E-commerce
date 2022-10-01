from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.models import User,auth
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
    if request.user.is_authenticated and request.user.is_superuser==False:
        return redirect('index')
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(request, username=username, password=password)
        if user is not None  and user.is_active and user.is_superuser==False:
            auth.login(request, user)
            
            return redirect('index')
        else:
            messages.info(request,"Invalid Credentials")
            return redirect('login')
    return render(request, 'user/login.html')

def index(request):
    product=Product.objects.all()
    categories=Category.objects.all()
    if request.user.is_authenticated:
        user=request.user
        print('user=',user)
        return render(request,'user/home.html',{'user':user,'products':product, 'categories':categories})
    else:
        return render(request, 'user/home.html',{'products':product,'categories':categories})

def signup(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        phone = request.POST['phone']
        email= request.POST['email']
        username = request.POST['username']
        password = request.POST['password']
        if User.objects.filter(username=username).exists():
            messages.info(request, 'Username Taken')
            return redirect('signup')
        user = User.objects.create_user(first_name=first_name, last_name=last_name,  username=username, email=email, password=password)
        user.save()
        user_id = User.objects.get(username=username)
        account = Accounts.objects.create(user=user_id, phone=phone)
        account.save()
        
        return redirect('login')
    else:
        return render(request, 'user/signup.html')
    
def view_product(request):
    id=request.GET['id']
    product=Product.objects.get(id=id)
    return render(request, 'user/view_product.html',{'product':product})

def minus(request):
    id=request.GET['id']
    cart=Cart.objects.get(id=id)
    qty=cart.quantity-1
    print(qty)
    Cart.objects.filter(id=id).update(quantity=qty)
    return redirect('cart')    

def up(request):
    id=request.GET['id']
    cart=Cart.objects.get(id=id)
    qty=cart.quantity+1
    print(qty)
    Cart.objects.filter(id=id).update(quantity=qty)
    return redirect('cart')
def getotp(request):
    phone=request.POST['phone']
    # Accounts.objects.get(phone=phone)
    
    # user=User.objects.filter(id=phone.user_id)
    if not Accounts.objects.filter(phone=phone).exists():
        messages.info(request,"Phone Number Not Registered")
        return redirect('login')
    else:
        number = Accounts.objects.get(phone=phone)
        num = Accounts.objects.filter(phone=phone)
        print('1',number.phone)
        user = User.objects.get(id=number.user_id)
        otp=random.randint(100000,999999)
        numb=Accounts.objects.filter(phone=phone).update(otp=otp)
        print(otp)
        
        message_handler = MessageHandler(phone,otp).sent_otp_on_phone()
        return render(request, 'user/otplogin.html',{'user':user})

def otplogin(request):
    id=request.GET['id']
    otp=request.POST['otp']
    user=User.objects.get(id=id)
    print(user.accounts.phone)
    if Accounts.objects.filter(otp=otp).exists():
        user = auth.authenticate(request, username=user.username, password=user.password)
        auth.login(request, user)
        return redirect('index')
    else:
        messages.info(request,"Invalid OTP")
        return redirect('login')
    
def cart(request):
    if request.user.is_authenticated:
        user=request.user
        cart= Cart.objects.filter(user=user) 
        for i in range(len(cart)):
            if cart[i].quantity<1:
                cart[i].delete()
            
        
        if len(cart)==0:
            empty="Cart is Empty"
            
            return render(request, 'user/cart.html',{'empty':empty})
        else:
            
            subtotal=0
            for i in range(len(cart)):
                x=cart[i].product.price*cart[i].quantity
                subtotal=subtotal+x
            shipping = 0
            total = subtotal+ shipping
            return render(request, 'user/cart.html',{'cart':cart,'subtotal':subtotal,'total':total})
    else:
        return redirect('login')
    
def checkout(request):
    return render(request, 'user/checkout.html')
@login_required(login_url=login)   
def addtocart(request):
    pid = request.GET['pid']
    product = Product.objects.get(id=pid)
    uid = request.user
    print("pid=",pid)
    print("uid =",uid)
    if Cart.objects.filter(product=pid, user=uid).exists():
        cart = Cart.objects.get(product=pid, user=uid)
        cart.quantity += 1
        cart.save()
        return redirect('cart')
    else:
        cart = Cart.objects.create(product=product, user=uid)
        cart= Cart.objects.filter(user=uid)
        # return render(request, 'user/cart.html',{'cart':cart})
        return redirect('cart')
    
def logout(request):
    # user=request.user
    auth.logout(request)
    return redirect('index')