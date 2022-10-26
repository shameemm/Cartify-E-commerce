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
    path('cancelorder',views.cancelorder, name='cancelorder'),
    path('updatestatus',views.updatestatus, name='updatestatus'),
    path('offers',views.offers, name='offers'),
    path('prod_addoffer',views.prod_addoffer, name='prod_addoffer'),
    path('cate_addoffer',views.cate_addoffer, name='cate_addoffer'),
    path('coupons',views.coupons, name='coupons'),
    path('addcoupon',views.addcoupon, name='addcoupon'),
    path('report',views.report, name='report'),
    path('blockcoupon',views.blockcoupon, name='blockcoupon'),
    path('unblockcoupon',views.unblockcoupon, name='unblockcoupon'),
    path('acceptrequest',views.acceptrequest, name='acceptrequest'),
    path('rejectrequest',views.rejectrequest, name='rejectrequest'),
    path('sales',views.sales, name='sales'),
    path('monthly',views.monthly, name='monthly'),
    path('yearly',views.yearly, name='yearly'),
    
]
    
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
