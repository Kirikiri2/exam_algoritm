from django.contrib.auth.models import User
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Task(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=500, null=True, blank=True)
    max_points = models.IntegerField()
    image = models.ImageField(upload_to='task_images/', blank=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Answer(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    add_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} – {self.task} – {self.add_date}"

class Grade(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    points = models.IntegerField()
    graded_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='grades_given')
    graded_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('task', 'user')

class AnswerEdit(models.Model):
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name='edits')
    edited_text = models.TextField()
    edit_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Edit of Answer {self.answer.id} on {self.edit_date}"
