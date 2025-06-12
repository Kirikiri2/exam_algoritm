from django import forms
from .models import Task, Answer, Grade

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['name', 'description', 'max_points', 'image']
        labels = {
            'name': 'Название задачи',
            'description': 'Описание',
            'max_points': 'Максимальное количество баллов',
            'image': 'Изображение'
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['text']
        labels = {'text': 'Ваш код на Python:'}
        widgets = {
            'text': forms.Textarea(attrs={
                'rows': 10,
                'cols': 80,
                'placeholder': '# Введите ваш код здесь',
                'style': 'font-family: monospace; background-color: #f5f5f5; border: 1px solid #ccc; padding: 10px;'
            })
        }

class GradeForm(forms.ModelForm):
    class Meta:
        model = Grade
        fields = ['points']
        labels = {'points': 'Баллы'}
        widgets = {
            'points': forms.NumberInput(attrs={
                'min': 0,
                'class': 'form-control',
                'style': 'width: 120px'
            })
        }

    def __init__(self, *args, **kwargs):
        self.task = kwargs.pop('task', None)
        super().__init__(*args, **kwargs)
        if self.task:
            self.fields['points'].widget.attrs['max'] = self.task.max_points
            help_text = f"Максимум: {self.task.max_points} баллов"
            self.fields['points'].help_text = help_text

    def clean_points(self):
        points = self.cleaned_data['points']
        if self.task and points > self.task.max_points:
            raise forms.ValidationError(
                f"Превышен максимальный балл ({self.task.max_points})"
            )
        return points
