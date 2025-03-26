from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import User
from PIL import Image
import os
from django.conf import settings
from django.core.files.storage import default_storage

class Expenses(models.Model):
    amount = models.FloatField()
    date = models.DateField(default=now)
    description = models.TextField()
    owner = models.ForeignKey(to=User, on_delete=models.CASCADE)
    category = models.CharField(max_length=256)
    transaction_type = models.CharField(max_length=10, choices=[('Expense', 'Expense'), ('Income', 'Income')])  # Changed from 'Expenses' to 'Expense'
    receipt = models.ImageField(upload_to='receipts/', null=True, blank=True)

    def __str__(self) -> str:
        return self.category
    
    def save(self, *args, **kwargs):
        # Compress receipt image before saving
        if self.receipt:
            super().save(*args, **kwargs)
            try:
                img = Image.open(self.receipt.path)
                if img.height > 800 or img.width > 800:
                    output_size = (800, 800)
                    img.thumbnail(output_size)
                    img.save(self.receipt.path, quality=70)
            except Exception as e:
                print(f"Error processing image: {e}")
        else:
            super().save(*args, **kwargs)

    class Meta:
        ordering = ["-date"]
        verbose_name_plural = "Expenses"

class Category(models.Model):
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=10, choices=[('EXPENSE', 'Expense'), ('INCOME', 'Income')], default='EXPENSE')

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self) -> str:
        return self.name

class Budget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Budget: {self.amount}"