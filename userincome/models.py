from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import User

class Income(models.Model):
    amount = models.FloatField()
    date = models.DateField(default=now)
    description = models.TextField(default="")  # Provide a default value
    owner = models.ForeignKey(to=User, on_delete=models.CASCADE)
    source = models.CharField(max_length=256)

    def __str__(self) -> str:
        return self.source
    
    class Meta:
        ordering = ["-date"]

class Source(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name_plural = "Sources"

    def __str__(self) -> str:
        return self.name