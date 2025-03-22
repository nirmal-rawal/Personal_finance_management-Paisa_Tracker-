from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import User

class Expenses(models.Model):
    amount = models.FloatField()
    date = models.DateField(default=now)
    description = models.TextField()
    owner = models.ForeignKey(to=User, on_delete=models.CASCADE)
    category = models.CharField(max_length=256)
    transaction_type = models.CharField(max_length=10, choices=[('Expenses', 'Expenses'), ('Income', 'Income')])

    def __str__(self) -> str:
        return self.category
    
    class Meta:
        ordering = ["-date"]

class Category(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self) -> str:
        return self.name