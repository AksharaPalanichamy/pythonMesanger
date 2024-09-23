from django.shortcuts import render,get_object_or_404
from django.contrib.auth.models import User

def chat_box(request, chat_box_name):
    # we will get the chatbox name from the url
    return render(request, "chatbox.html", {"chat_box_name": chat_box_name})
    # target_username = chat_box_name.split('_')[0]  # Adjust as needed
    # target_user = get_object_or_404(User, username=target_username)

    # return render(request, 'chat.html', {
    #     'chat_box_name': chat_box_name,
    #     'target_user': target_user.username,
    # })
