from django.shortcuts import render, redirect, get_object_or_404
from .models import User, Task, Answer, AnswerEdit, Grade
from .forms import TaskForm, AnswerForm, GradeForm
from django.utils.timezone import now
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.admin.views.decorators import staff_member_required 

def is_admin(user):
    return user.is_superuser

def index(request):
    if not request.user.is_authenticated:
        return render(request, 'exams/index.html')

    if request.user.is_superuser:
        users = User.objects.exclude(id=request.user.id)
        tasks = Task.objects.count()
        user_progress = []
        all_tasks = Task.objects.all()
        for user in users:
            solved_tasks = Answer.objects.filter(user=user).values('task').distinct().count()
            grades = Grade.objects.filter(user=user)

            earned_points = sum([g.points for g in grades if g.points is not None])
            max_points = sum([task.max_points for task in all_tasks])

            user_progress.append({
                'user': user,
                'solved': solved_tasks,
                'total': tasks,
                'points': earned_points,
                'max_points': max_points,
            })

        context = {'user_progress': user_progress}
        return render(request, 'exams/admin_dashboard.html', context)
    else:
        total_tasks = Task.objects.count()
        solved_tasks = Answer.objects.filter(user=request.user).values('task').distinct().count()
        remaining_tasks = total_tasks - solved_tasks
        context = {
        'user': request.user,
        'total_tasks': total_tasks,
        'remaining_tasks': remaining_tasks,
    }
        return render(request, 'exams/user_dashboard.html', context)


@staff_member_required
def user_profile(request, user_id):
    profile_user = get_object_or_404(User, pk=user_id)
    tasks = Task.objects.all()

    statuses = []
    for task in tasks:
        answer = Answer.objects.filter(user=profile_user, task=task).order_by('-add_date').first()
        grade = Grade.objects.filter(user=profile_user, task=task).first()

        if grade:
            status = "Проверена"
        elif answer:
            status = "В работе"
        else:
            status = "Не решена"

        statuses.append({
            'task': task,
            'answer': answer,
            'status': status,
            'grade': grade,
        })

    context = {
        'profile_user': profile_user,
        'statuses': statuses,
    }
    return render(request, 'exams/user_profile.html', context)


@staff_member_required
def grade_task(request, user_id, task_id):
    user = get_object_or_404(User, id=user_id)
    task = get_object_or_404(Task, id=task_id)

    grade, created = Grade.objects.get_or_create(
        user=user,
        task=task,
        defaults={'points': 0, 'graded_by': request.user}
    )

    if request.method == 'POST':
        form = GradeForm(request.POST, instance=grade, task=task)
        if form.is_valid():
            grade = form.save(commit=False)
            grade.graded_by = request.user
            grade.save()
            return redirect('exams:user_profile', user_id=user.id)
    else:
        form = GradeForm(instance=grade, task=task)

    answers = Answer.objects.filter(user=user, task=task).order_by('-add_date')

    context = {
        'form': form,
        'user': user,
        'task': task,
        'answers': answers,
        'max_points': task.max_points,
    }
    return render(request, 'exams/grade_task.html', context)

@login_required
def tasks(request):
    tasks = Task.objects.order_by('name')
    answered_task_ids = set(Answer.objects.filter(user=request.user).values_list('task_id', flat=True).distinct())

    grades = Grade.objects.filter(user=request.user)
    grades_map = {grade.task_id: grade.points for grade in grades}

    tasks_data = []
    for task in tasks:
        tasks_data.append({
            'task': task,
            'answered': task.id in answered_task_ids,
            'points': grades_map.get(task.id),
        })

    context = {
        'tasks_data': tasks_data,
    }
    return render(request, 'exams/tasks.html', context)


def task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    user_answers = Answer.objects.filter(task=task, user=request.user).order_by('-add_date')
    try:
        grade = Grade.objects.get(task=task, user=request.user)
    except Grade.DoesNotExist:
        grade = None

    if request.method == 'POST':
        form = AnswerForm(request.POST)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.task = task
            answer.user = request.user
            answer.add_date = now()
            answer.save()
            return redirect('exams:task', task_id=task.id)
    else:
        form = AnswerForm()

    context = {
        'task': task,
        'form': form,
        'user_answers': user_answers,
        'grade': grade,
    }
    return render(request, 'exams/task.html', context)

@user_passes_test(is_admin)
def new_task(request):
    if request.method != 'POST':
        form = TaskForm()
    else:
        form = TaskForm(request.POST, request.FILES)
        if form.is_valid():
            new_task = form.save(commit=False)
            new_task.owner = request.user
            new_task.save()
            return redirect('exams:tasks')

    context = {'form': form}
    return render(request, 'exams/new_task.html', context)

def edit_answer(request, answer_id):
    answer = get_object_or_404(Answer, id=answer_id, user=request.user)
    task = answer.task

    if request.method != 'POST':
        form = AnswerForm(instance=answer)
    else:
        form = AnswerForm(request.POST, instance=answer)
        if form.is_valid():
            AnswerEdit.objects.create(
                answer=answer,
                edited_text=answer.text,
            )
            form.save()
            return redirect('exams:task', task_id=task.id)
    context = {'form': form, 'answer': answer}
    return render(request, 'exams/edit_answer.html', context)

@staff_member_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    if request.method == 'POST':
        task.delete()
        return redirect('exams:tasks') 
    return render(request, 'exams/confirm_delete_task.html', {'task': task})

@staff_member_required
def edit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    if request.method == 'POST':
        form = TaskForm(request.POST, request.FILES, instance=task)
        if form.is_valid():
            form.save()
            return redirect('exams:tasks')
    else:
        form = TaskForm(instance=task)

    return render(request, 'exams/edit_task.html', {'form': form, 'task': task})
