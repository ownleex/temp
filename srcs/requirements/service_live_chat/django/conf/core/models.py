from django.db import models
from shared_models.models import Player

class GeneralMessage(models.Model):
    sender = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='general_messages')
    content = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"General Chat: {self.sender.name} - {self.content}"

class PrivateMessage(models.Model):
    sender = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='sent_private_messages')
    receiver = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='received_private_messages')
    content = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.sender.name} to {self.receiver.name}: {self.content}"
