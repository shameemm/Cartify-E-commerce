from django.db import models
from django.contrib.auth.models import User
from .admin.models import *
# Create your models here.
class Accounts(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.BigIntegerField()
    
    def __str__(self):
        return self.user.username