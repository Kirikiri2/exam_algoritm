from django.contrib import admin
from .models import Task, Answer, AnswerEdit

admin.site.register(Task)
admin.site.register(Answer)
admin.site.register(AnswerEdit)