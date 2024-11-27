from django.db import models
from django.contrib.auth.models import User

class Question(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='questions')
    title = models.CharField(max_length=255)
    question = models.TextField()
    date = models.DateField()

    def __str__(self) -> str:
        return self.title