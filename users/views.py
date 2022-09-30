from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.models import User,auth
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from accounts.models import Accounts
from admins.models import *
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
        otp=random.randint(1000,9999)
        numb=Accounts.objects.filter(phone=phone).update(otp=otp)
        print(otp)
        
        # message_handler = MessageHandler(phone,otp).sent_otp_on_phone()
        return render(request, 'user/otplogin.html',{'user':user})

def otplogin(request):
    id=request.GET['id']
    otp=request.POST['otp']
    if Accounts.objects.filter(otp=otp).exists():
        user=User.objects.get(id=id)
        auth.login(request, user)
        return redirect('index')
    else:
        messages.info(request,"Invalid OTP")
        return redirect('login')
def logout(request):
    # user=request.user
    auth.logout(request)
    return redirect('index')