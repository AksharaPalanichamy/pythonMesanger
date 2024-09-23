from django.shortcuts import render,get_object_or_404
from django.contrib.auth.models import User
from .models import ChatRoom
def chat_box(request, chat_box_name):
    # we will get the chatbox name from the url
    ##return render(request, "chatbox.html", {"chat_box_name": chat_box_name})
    current_user = request.user.username
    # Check if a ChatRoom with this name exists, create if it doesn't

    # For direct messaging, get the target user if chat_box_name is a username
    try:
        target_user = User.objects.get(username=chat_box_name)
    except User.DoesNotExist:
        target_user = None  # Or handle differently if needed

    chat_box_name=generate_room_name(current_user, target_user.username)
    chat_room, created = ChatRoom.objects.get_or_create(name=chat_box_name)

    return render(request, 'chatbox.html', {
        'chat_box_name': chat_room.name,
        'target_user': target_user.username if target_user else None,
    })

def generate_room_name(user1, user2):
    return f"{min(user1, user2)}_{max(user1, user2)}"