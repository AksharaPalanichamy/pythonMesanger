from django.contrib import admin
from .models import ChatRoom

##admin.site.register(ChatRoom)
admin.autodiscover()
admin.site.enable_nav_sidebar = False