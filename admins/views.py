from django.shortcuts import render, redirect
from django.contrib import messages
from .models import *
from users.models import *
import os
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.models import User, auth
from django.contrib.auth.decorators import login_required
# Create your views here.
def adminlogin(request):
    if request.user.is_authenticated and request.user.is_superuser:
        return redirect('adminhome')
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate( username=username, password=password)
        if user is not None and user.is_superuser==True:
            auth.login(request, user)
            return redirect('adminhome')
        else:
            print(password)
            messages.info(request, 'Invalid Cedentials')
            return redirect('adminlogin')
    else:
        return render(request, 'admins/admin_login.html')
    
def addcategory(request):
    if request.method == 'POST':
        name = request.POST['name']
        description = request.POST['description']
        category = Category.objects.create(name=name,description=description)
        category.save()
        return redirect('categories')
    else:
        return render(request, 'admins/add_category.html')
    
@login_required(login_url='adminlogin')
def category_block(request):
    id=request.GET['id']
    category=Category.objects.get(id=id)
    category.is_active=False
    print(category)
    category.save()
    return redirect('categories')

@login_required(login_url='adminlogin')
def category_unblock(request):
    id=request.GET['id']
    category=Category.objects.get(id=id)
    category.is_active=True
    print(category)
    category.save()
    return redirect('categories')

@login_required(login_url='adminlogin')
def delete_category(request):
    id=request.GET['id']
    category=Category.objects.filter(id=id)
    category.delete()
    return redirect('categories')

@login_required(login_url='adminlogin')    
def adminhome(request):
    return render(request, 'admins/admin_home.html')


@login_required(login_url='adminlogin')
def users(request):
    users = User.objects.filter(is_superuser=False)
    return render(request, 'admins/user_management.html', {'users':users})

@login_required(login_url='adminlogin')
def addproduct(request):
    if request.method == 'POST':
        name = request.POST['name']
        description = request.POST['description']
        price = request.POST['price']
        category = request.POST['category']
        brand = request.POST['brand']
        print(request.FILES,"  1111")
        image = request.FILES['image']
        
        category=Category.objects.get(id=category)
        product = Product.objects.create(name=name,description=description,price=price,category=category,image=image,brand=brand)
        product.save()
        return redirect('products')
    else:
        
        category=Category.objects.all()
        return render(request, 'admins/add_product.html',{'categories':category})
    
@login_required(login_url='adminlogin')
def products(request):
    product=Product.objects.all()
    
    return render(request, 'admins/product_management.html',{'products':product})
@login_required(login_url='adminlogin')
def order(request):
    order = Order.objects.all()
    cart = Cart.objects.all()
    return render(request, 'admins/ordermanagement.html',{'orders':order,'carts':cart})

@login_required(login_url='adminlogin')
def delete_product(request):
    id=request.GET['id']
    product=Product.objects.filter(id=id)
    product.delete()
    return redirect('products')

@login_required(login_url='adminlogin')
def edit_product(request):
    id=request.GET['id']
    prod = Product.objects.get(id=id)
    if request.method=='POST':
        id=request.GET['id']
        prod = Product.objects.get(id=id)
        print(id)
        
        name = request.POST['name']
        description = request.POST['description']
        price = request.POST['price']
        category = request.POST['category']
        brand = request.POST['brand']
        print(request.FILES,"  1111")
        image = request.FILES['image']
        
        category=Category.objects.get(id=category)
        product = Product.objects.get(id=id)
        product.name=name
        product.description=description
        product.price=price
        product.category=category
        product.brand=brand
        
        product.image=image
        product.save()
        
        return redirect('products')
    else:
        id=request.GET['id']
        product=Product.objects.get(id=id)
        category=Category.objects.all()
        return render(request, 'admins/edit_product.html',{'product':product,'categories':category})
@login_required(login_url='adminlogin')
def block(request):
    id=request.GET['id']
    user=User.objects.get(id=id)
    user.is_active=False
    user.save()
    return redirect('users')
@login_required(login_url='adminlogin')
def unblock(request):
    id=request.GET['id']
    user=User.objects.get(id=id)
    user.is_active=True
    user.save()
    return redirect('users')
@login_required(login_url='adminlogin')
def categories(request):
    category=Category.objects.all()
    return render(request, 'admins/category_management.html',{'categories':category})
@login_required(login_url='adminlogin')
def adminlogout(request):
    auth.logout(request)
    return redirect('adminlogin')