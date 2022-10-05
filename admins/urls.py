from django.urls import path
from . import views

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    
    path('',views.adminlogin, name='adminlogin'),
    path('adminhome',views.adminhome, name='adminhome'),
    path('users',views.users, name='users'),
    path('block',views.block,name='block'),
    path('unblock',views.unblock,name='unblock'),
    path('products',views.products, name='products'),
    path('category',views.categories, name='categories'),
    path('adminlogout',views.adminlogout, name='adminlogout'),
    path('addcategory',views.addcategory,name='addcategory'),
    path('delete_category',views.delete_category,name='delete_category'),
    path('category_block',views.category_block,name='category_block'),
    path('category_unblock',views.category_unblock,name='category_unblock'),
    path('addproduct',views.addproduct,name='addproduct'),
    path('deleteproduct',views.delete_product,name='delete_product'),
    path('editproduct',views.edit_product,name='edit_product'),
    path('order',views.order, name='order'),
]
    
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
