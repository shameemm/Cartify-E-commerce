from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('login', views.login, name='login'),
    path('signup',views.signup, name='signup'),
    path('',views.index, name='index'),
    path('logout',views.logout, name='logout'),
    path('view_product',views.view_product, name='view_product'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)