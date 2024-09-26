"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings
from django.urls import path
from app.views import chat_box,register,CustomLoginView,block_users_view,delete_chat_rooms_view,create_users_view
from django.contrib.auth import views as auth_views
from app.admin import admin_site
urlpatterns = [
    path("admin/", admin_site.urls),
    path("chat/<str:chat_box_name>/", chat_box, name="chat_box"),
    path('register/', register, name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('admin/block-users/', block_users_view, name='block_users'),
    path('admin/delete-chat-rooms/', delete_chat_rooms_view, name='delete_chat_rooms'),
    path('admin/create-users/', create_users_view, name='create_users'),
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)