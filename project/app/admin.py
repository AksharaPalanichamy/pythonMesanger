from django.contrib import admin
from .models import ChatRoom
from django.urls import path
from .views import block_users_view, delete_chat_rooms_view, create_users_view

# ##admin.site.register(ChatRoom)
# admin.autodiscover()
# admin.site.enable_nav_sidebar = False

class MyAdminSite(admin.AdminSite):
    site_header = "SecureIM Admin"
    site_title = "Admin Portal"
    index_title = "Welcome to the Admin Portal"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('block-users/', self.admin_view(block_users_view), name='block_users'),
            path('delete-chat-rooms/', self.admin_view(delete_chat_rooms_view), name='delete_chat_rooms'),
            path('create-users/', self.admin_view(create_users_view), name='create_users'),
        ]
        return custom_urls + urls

admin_site = MyAdminSite(name='myadmin')
admin.site.register(ChatRoom)