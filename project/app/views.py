from django.shortcuts import render,get_object_or_404,redirect
from django.contrib.auth.models import User
from .models import ChatRoom,Message
from django.db.models import Q
from .forms import UserRegistrationForm
from django.contrib.auth import login,authenticate
from django.contrib.auth.views import LoginView
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test,login_required
from django.contrib.auth.forms import AuthenticationForm

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
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
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

    if request.method == 'POST':
            message_content = request.POST.get('message')  # Assuming this is the text message
            file = request.FILES.get('file')  # Get the uploaded file

            # Create a new message instance
            Message.objects.create(room=chat_room, user=request.user, encrypted_message=message_content, file=file)

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

@user_passes_test(lambda u: u.is_superuser) 
def block_users_view(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        try:
            user = User.objects.get(id=user_id)
            user.is_active = False  # Deactivate the user account
            user.save()
            messages.success(request, f'User {user.username} has been blocked.')
        except User.DoesNotExist:
            messages.error(request, 'User not found.')
    
    users = User.objects.filter(is_active=True)  # List only active users
    context = {
        'users': users,
        'site_title': 'Admin Portal',  # Custom site title
        'site_header': 'SecureIM Admin',  # Custom site header
        'show_home_button':True
    }
    return render(request, 'admin/block_users.html', context)

@user_passes_test(lambda u: u.is_superuser) 
def delete_chat_rooms_view(request):
    if request.method == 'POST':
        room_id = request.POST.get('room_id')
        try:
            chat_room = ChatRoom.objects.get(id=room_id)
            chat_room.delete()
            messages.success(request, 'Chat room has been deleted.')
        except ChatRoom.DoesNotExist:
            messages.error(request, 'Chat room not found.')

    chat_rooms = ChatRoom.objects.all()  # List all chat rooms
    context = {
        'chat_rooms': chat_rooms,
        'site_title': 'Admin Portal',  # Custom site title
        'site_header': 'SecureIM Admin',  # Custom site header
        'show_home_button':True
    }
    return render(request, 'admin/delete_chat_rooms.html', context)

@user_passes_test(lambda u: u.is_superuser) 
def create_users_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        is_admin=request.POST.get('is_admin')
        try:
            if is_admin:
                user=User.objects.create_superuser(username=username,email=email,password=password)
            else:
                user = User.objects.create_user(username=username,email=email, password=password)
            user.save()
            messages.success(request, f'User {username} has been created.')
            return redirect('admin:create_users')  # Redirect to admin index after successful creation
        except Exception as e:
            messages.error(request, str(e))
    context = {
        'site_title': 'Admin Portal',  # Set your site title
        'site_header': 'SecureIM Admin',  # Set your site header
        'show_home_button':True
    }
    return render(request, 'admin/create_users.html',context)

def custom_admin_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None and user.is_staff:
                login(request, user)
                return redirect('/admin/')  # Redirect to admin dashboard
            else:
                messages.error(request, 'Invalid credentials or not an admin user.')
    else:
        form = AuthenticationForm()
    return render(request, 'admin/login.html', {'form': form})