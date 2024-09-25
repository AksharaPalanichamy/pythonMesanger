from django.shortcuts import render,get_object_or_404
from django.contrib.auth.models import User
from .models import ChatRoom,Message
from django.db.models import Q

def chat_box(request, chat_box_name):

    current_user = request.user.username
   # Get all users for the search functionality
    all_users = User.objects.exclude(username=current_user)

    chat_rooms = ChatRoom.objects.filter(
        Q(name__startswith=current_user) | Q(name__endswith=current_user)
    )

    chat_users = []
    for room in chat_rooms:
        # Extract the other user from the room name
        room_users = room.name.split('_')
        other_user = room_users[0] if room_users[1] == current_user else room_users[1]
        chat_users.append(User.objects.get(username=other_user))

    # For direct messaging, get the target user if chat_box_name is a username
    try:
        target_user = User.objects.get(username=chat_box_name)
    except User.DoesNotExist:
        target_user = None  # Or handle differently if needed

    chat_box_name=generate_room_name(current_user, target_user.username if target_user else "")
    chat_room, created = ChatRoom.objects.get_or_create(name=chat_box_name)

    messages = Message.objects.filter(room=chat_room).order_by('timestamp')

    return render(request, 'chatbox.html', {
        'chat_box_name': chat_room.name,
        'target_user': target_user.username if target_user else None,
        'messages': messages,
        'chat_users': chat_users,
        'all_users': all_users,
    })

def generate_room_name(user1, user2):
    return f"{min(user1, user2)}_{max(user1, user2)}"