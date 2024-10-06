
from django.db import models
from django.contrib.auth.models import User
from cryptography.fernet import Fernet
from django.conf import settings

SECRET_KEY = settings.SECRET_CHAT_KEY
class ChatRoom(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name
    
class Message(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    encrypted_message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to='uploads/', blank=True, null=True)

    def __str__(self):
        return f'{self.user.username}: {self.message[:50]}'
    
    def encrypt_message(self, message):
        """Encrypt the message before saving."""
        f = Fernet(SECRET_KEY.encode())
        encrypted_message = f.encrypt(message.encode())
        return encrypted_message.decode()

    def decrypt_message(self):
        """Decrypt the message when reading."""
        f = Fernet(SECRET_KEY.encode())
        decrypted_message = f.decrypt(self.encrypted_message.encode())
        return decrypted_message.decode()

    def save(self, *args, **kwargs):
        # Encrypt the message before saving
        if not self.pk:  # Only encrypt if creating a new message
            self.encrypted_message = self.encrypt_message(self.encrypted_message)
        super().save(*args, **kwargs)

    @property
    def message(self):
        """Retrieve the decrypted message."""
        return self.decrypt_message()