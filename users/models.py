from django.db import models
from django.contrib.auth.models import User
from admins.models import *
# Create your models here.

class Cart(models.Model):
    quantity = models.IntegerField(default=1)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    cancel = models.BooleanField(default=False)
    
    
    def __str__(self):
        return self.product.name
    
class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    #  order = models.ForeignKey(Order, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.IntegerField()
    
    def __str__(self):
        return self.user.username    
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # product = models.ForeignKey(Product, on_delete=models.CASCADE)
    address = models.ForeignKey(Address, on_delete=models.CASCADE)
    # quantity = models.IntegerField(default=1)
    ordered_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=100, default='Order Confirmed')
    amount = models.FloatField(default=1)
    method = models.CharField(max_length=100, default='Cash On Delivery')
    cancel = models.BooleanField(default=False)
    reason = models.CharField(max_length=200, default='')
    
    
    
    
    # def __str__(self):
    #     return self.product.name
    
# class Payment(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     order = models.ForeignKey(Order, on_delete=models.CASCADE)
#     amount = models.FloatField()
#     method = models.CharField(max_length=100)
#     status = models.CharField(max_length=100, default='pending')
    
#     def __str__(self):
#         return self.user.username

class OldCart(models.Model):
    quantity = models.IntegerField(default=1)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    cancel = models.BooleanField(default=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, default=0)
    
    def __str__(self):
        return self.product.name
    

