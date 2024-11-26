from django.db import models

class Question(models.Model):
    title = models.CharField(max_length=255)
    question = models.TextField()
    date = models.DateField()

    def __str__(self) -> str:
        return self.title