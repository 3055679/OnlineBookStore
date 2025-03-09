# from users import views
from django.shortcuts import redirect;
from django.contrib import admin
from django.urls import include, path
from users import views as user_views
from django.contrib.auth import views as authentication_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('bookstore/', include('bookstore.urls')),
    path('register/',user_views.register, name='register'),
    # path('login/',authentication_views.LoginView.as_view(template_name='users/login.html'),name='login'),
    # path('login/', authentication_views.LoginView.as_view(template_name='users/login.html', redirect_authenticated_user=True), name='login'),
    # path('logout/',authentication_views.LogoutView.as_view(template_name='users/logout.html'),name='logout'),
    path('login/', user_views.custom_login, name='login'),  # Custom login view
    path('logout/', user_views.custom_logout, name='logout'),  # Custom logout view
    path('forgot_password/', user_views.forgot_password, name='forgot_password'),
    
    path('', lambda request: redirect('/bookstore/home/', permanent=True)),
    


]
