from django.db import models
from django.contrib.auth.models import User
from admins.models import *
# Create your models here.

class Cart(models.Model):
    quantity = models.IntegerField(default=1)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    
    
    def __str__(self):
        return self.product.name
    