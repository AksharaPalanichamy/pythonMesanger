from django.shortcuts import render,get_object_or_404,redirect
from django.contrib.auth.models import User
from .models import ChatRoom,Message
from django.db.models import Q
from .forms import UserRegistrationForm
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.urls import reverse


class CustomLoginView(LoginView):
    template_name = 'registration/login.html'  # Specify your login template

    def get_success_url(self):
        # Redirect to a specific chat box
        user = self.request.user
        first_chat_room = ChatRoom.objects.filter(Q(name__startswith=user.username) | Q(name__endswith=user.username)).first()
        if first_chat_room:
            return reverse('chat_box', kwargs={'chat_box_name': first_chat_room.name})
        return reverse('chat_box', kwargs={'chat_box_name': 'default_room_name'})  # Fallback
    
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])  # Hash the password
            user.save()
            ##login(request, user)  # Automatically log in the user
            return redirect('login')  # Redirect to a home page or wherever you want
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})


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

        if len(room_users) < 2:  # Ensure there are at least two users in the room name
            continue  # Skip this room if it doesn't have the expected format
        
        if room_users[1] == current_user:
            other_user = room_users[0]
        else:
            other_user = room_users[1]
        chat_users.append(User.objects.get(username=other_user))

    target_user = None
    # For direct messaging, get the target user if chat_box_name is a username
    try:
        target_user = User.objects.get(username=chat_box_name)
    except User.DoesNotExist:
        target_user = None  # Or handle differently if needed

    if target_user:
        chat_box_name = generate_room_name(current_user, target_user.username)
    else:
        chat_box_name = generate_room_name(current_user, '')  # Or some fallback logic
        
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
    if not user2:  # If user2 is None or empty
        return user1  # Just return user1 as the room name
    return f"{min(user1, user2)}_{max(user1, user2)}"