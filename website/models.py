from django.db import models
from django.contrib.auth.models import User

################# QUESTIONS #################
class Question(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='questions')
    title = models.CharField(max_length=255)
    question = models.TextField()
    date = models.DateField()

    def __str__(self) -> str:
        return self.title

################# ANSWER #################
class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='answers')
    content = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Answer by {self.author.username} to {self.question.title}"