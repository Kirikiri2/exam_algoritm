from django.urls import path
from . import views

app_name = 'exams'
urlpatterns = [
    path('', views.index, name='index'),
    path('tasks/', views.tasks, name='tasks'),
    path('new_task/', views.new_task, name='new_task'),
    path('tasks/<int:task_id>/', views.task, name='task'),
    path('edit_answer/<int:answer_id>/', views.edit_answer, name='edit_answer'),
    path('user/<int:user_id>/', views.user_profile, name='user_profile'),
    path('admin_dashboard/', views.index, name='admin_dashboard'),
    path('grade/<int:user_id>/<int:task_id>/', views.grade_task, name='grade_task'),
    path('user_dashboard/', views.index, name='user_dashboard'),
    path('task/<int:task_id>/delete/', views.delete_task, name='delete_task'),
    path('tasks/<int:task_id>/edit/', views.edit_task, name='edit_task'),



    
]