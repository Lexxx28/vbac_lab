from django.db import models
from django.contrib.auth.models import User

class Page(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('publish', 'Published'),
        ('private', 'Private'),
    ]
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pages')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

