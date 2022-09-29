from django.contrib import admin
from accounts.models import Accounts
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

 
# class AccountInLine(admin.StackedInline):
#     model = Accounts
#     can_delete = False
#     verbose_name_plural = 'Accounts'
    
# class CostomizedUserAdmin(UserAdmin):
#     inlines = (AccountInLine, )
    
# admin.site.unregister(User)
# admin.site.register(User, AccountInLine)
admin.site.register(Accounts)