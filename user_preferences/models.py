from django.db import models
from django.contrib.auth.models import User

class UserPreference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # One-to-One relationship with User
    currency = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s preferences"