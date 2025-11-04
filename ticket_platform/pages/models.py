from django.db import models
from django.utils import timezone

class SupportMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    response = models.TextField(blank=True, null=True)
    is_support = models.BooleanField(default=False)  # True dacă mesajul e de la suport
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.name} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"


