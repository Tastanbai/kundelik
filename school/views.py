import os
from django.dispatch import receiver
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.contrib import messages
from mysite import settings
from .forms import UserRegistrationForm, LoginForm
from .models import SchoolUser, School, Grade, SubGrade, Subject, Lesson

DAYS_OF_WEEK = [
    (1, 'Понедельник'),
    (2, 'Вторник'),
    (3, 'Среда'),
    (4, 'Четверг'),
    (5, 'Пятница'),
    (6, 'Суббота'),
]

# Регистрация пользователя
def user_register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = User.objects.create_user(
                username=cd['username'],
                first_name=cd['first_name'],
                email=cd['email'],
                password=cd['password']
            )
            # Создаем уникальную школу для каждого пользователя
            user_school = School.objects.create(name=f"Школа {user.username}")
            SchoolUser.objects.create(user=user, school=user_school)

            # Создаем классы только один раз для новой школы
            if not Grade.objects.filter(school=user_school).exists():
                for i in range(1, 12):
                    Grade.objects.create(number=i, school=user_school)

            messages.success(request, "Регистрация прошла успешно. Теперь вы можете войти.")
            return redirect('user_login')
        else:
            messages.error(request, "Ошибка регистрации. Проверьте введённые данные.")
    else:
        form = UserRegistrationForm()
    return render(request, 'school/user_register.html', {'form': form})

# Логин пользователя
def user_login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request, username=cd['username'], password=cd['password'])
            if user is not None:
                login(request, user)
                messages.success(request, "Вы успешно вошли в систему.")
                return redirect('grade_list')
            else:
                messages.error(request, "Неверный логин или пароль.")
    else:
        form = LoginForm()
    return render(request, 'school/user_login.html', {'form': form})

# Логаут пользователя
@login_required
def user_logout_view(request):
    logout(request)
    messages.success(request, "Вы успешно вышли из системы.")
    return redirect('user_login')


@login_required
def subgrade_list(request, grade_id):
    user_school = request.user.school_user.school
    grade = get_object_or_404(Grade, id=grade_id, school=user_school)
    subgrades = grade.subgrades.all().order_by('letter')
    return render(request, 'school/subgrade_list.html', {'grade': grade, 'subgrades': subgrades})

# Расписание для конкретного подкласса
@login_required
def lesson_schedule(request, subgrade_id):
    user_school = request.user.school_user.school
    subgrade = get_object_or_404(SubGrade, id=subgrade_id, grade__school=user_school)
    lessons_by_day = {}
    for day_num, day_name in DAYS_OF_WEEK:
        lessons = Lesson.objects.filter(subgrade=subgrade, day_of_week=day_num).order_by('start_time')
        lessons_by_day[day_name] = lessons
    return render(request, 'school/lesson_schedule.html', {'subgrade': subgrade, 'lessons_by_day': lessons_by_day})

# Кастомная админ-панель
@login_required
def custom_admin_dashboard(request):
    user_school = request.user.school_user.school
    context = {
        'school': user_school
    }
    return render(request, 'school/admin/dashboard.html', context)

# Управление предметами
@login_required
def manage_subjects(request):
    user_school = request.user.school_user.school
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            Subject.objects.create(name=name, school=user_school)
            messages.success(request, f"Предмет '{name}' добавлен.")
        else:
            messages.error(request, "Название предмета не может быть пустым.")
        return redirect('manage_subjects')
    subjects = Subject.objects.filter(school=user_school).order_by('name')
    return render(request, 'school/admin/manage_subjects.html', {'subjects': subjects})

# Добавление предмета (опционально, если используется отдельная страница для добавления)
@login_required
def add_subject(request):
    user_school = request.user.school_user.school
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            Subject.objects.create(name=name, school=user_school)
            messages.success(request, f"Предмет '{name}' добавлен.")
            return redirect('manage_subjects')
        else:
            messages.error(request, "Название предмета не может быть пустым.")
    return render(request, 'school/admin/add_subject.html')

# Удаление предмета
@login_required
def delete_subject(request, subject_id):
    user_school = request.user.school_user.school
    subject = get_object_or_404(Subject, id=subject_id, school=user_school)
    subject.delete()
    messages.success(request, f"Предмет '{subject.name}' удалён.")
    return redirect('manage_subjects')

# Управление подклассами
@login_required
def manage_subgrades(request):
    user_school = request.user.school_user.school
    if request.method == 'POST':
        grade_id = request.POST.get('grade_id')
        letter = request.POST.get('letter')
        grade = get_object_or_404(Grade, id=grade_id, school=user_school)
        if letter:
            letter = letter.upper()
            # Проверка уникальности подкласса
            if not SubGrade.objects.filter(grade=grade, letter=letter).exists():
                SubGrade.objects.create(grade=grade, letter=letter)
                messages.success(request, f"Подкласс '{grade.number}{letter}' добавлен.")
            else:
                messages.error(request, f"Подкласс '{grade.number}{letter}' уже существует.")
        else:
            messages.error(request, "Буква подкласса не может быть пустой.")
        return redirect('manage_subgrades')
    subgrades = SubGrade.objects.filter(grade__school=user_school).select_related('grade').order_by('grade__number', 'letter')
    grades = Grade.objects.filter(school=user_school).order_by('number')
    return render(request, 'school/admin/manage_subgrades.html', {'subgrades': subgrades, 'grades': grades})

# Добавление подкласса (опционально)
@login_required
def add_subgrade(request):
    user_school = request.user.school_user.school
    if request.method == 'POST':
        grade_id = request.POST.get('grade_id')
        letter = request.POST.get('letter')
        grade = get_object_or_404(Grade, id=grade_id, school=user_school)
        if letter:
            letter = letter.upper()
            if not SubGrade.objects.filter(grade=grade, letter=letter).exists():
                SubGrade.objects.create(grade=grade, letter=letter)
                messages.success(request, f"Подкласс '{grade.number}{letter}' добавлен.")
                return redirect('manage_subgrades')
            else:
                messages.error(request, f"Подкласс '{grade.number}{letter}' уже существует.")
        else:
            messages.error(request, "Буква подкласса не может быть пустой.")
    grades = Grade.objects.filter(school=user_school).order_by('number')
    return render(request, 'school/admin/add_subgrade.html', {'grades': grades})

# Удаление подкласса
@login_required
def delete_subgrade(request, subgrade_id):
    user_school = request.user.school_user.school
    subgrade = get_object_or_404(SubGrade, id=subgrade_id, grade__school=user_school)
    subgrade.delete()
    messages.success(request, f"Подкласс '{subgrade}' удалён.")
    return redirect('manage_subgrades')

# Управление уроками
@login_required
def manage_lessons(request):
    user_school = request.user.school_user.school
    if request.method == 'POST':
        subgrade_id = request.POST.get('subgrade_id')
        subject_id = request.POST.get('subject_id')
        day_of_week = request.POST.get('day_of_week')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')

        subgrade = get_object_or_404(SubGrade, id=subgrade_id, grade__school=user_school)
        subject = get_object_or_404(Subject, id=subject_id, school=user_school)

        # Проверка на пересечение времени уроков
        overlapping_lessons = Lesson.objects.filter(
            subgrade=subgrade,
            day_of_week=day_of_week,
            start_time__lt=end_time,
            end_time__gt=start_time
        )
        if overlapping_lessons.exists():
            messages.error(request, "Урок пересекается с другим уроком.")
        else:
            Lesson.objects.create(
                subgrade=subgrade,
                subject=subject,
                day_of_week=day_of_week,
                start_time=start_time,
                end_time=end_time
            )
            messages.success(request, f"Урок '{subject.name}' добавлен в {dict(DAYS_OF_WEEK)[int(day_of_week)]}.")
        return redirect('manage_lessons')

    lessons = Lesson.objects.filter(subgrade__grade__school=user_school).select_related('subgrade', 'subject').order_by('day_of_week', 'start_time')
    subgrades = SubGrade.objects.filter(grade__school=user_school).order_by('grade__number', 'letter')
    subjects = Subject.objects.filter(school=user_school).order_by('name')
    return render(request, 'school/admin/manage_lessons.html', {
        'lessons': lessons,
        'subgrades': subgrades,
        'subjects': subjects,
        'days': DAYS_OF_WEEK,
    })

@login_required
def add_lesson(request):
    user_school = request.user.school_user.school
    if request.method == 'POST':
        subgrade_id = request.POST.get('subgrade_id')
        subject_id = request.POST.get('subject_id')
        day_of_week = request.POST.get('day_of_week')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')

        subgrade = get_object_or_404(SubGrade, id=subgrade_id, grade__school=user_school)
        subject = get_object_or_404(Subject, id=subject_id, school=user_school)

        # Проверка на пересечение времени уроков
        overlapping_lessons = Lesson.objects.filter(
            subgrade=subgrade,
            day_of_week=day_of_week,
            start_time__lt=end_time,
            end_time__gt=start_time
        )
        if overlapping_lessons.exists():
            messages.error(request, "Урок пересекается с другим уроком.")
        else:
            Lesson.objects.create(
                subgrade=subgrade,
                subject=subject,
                day_of_week=day_of_week,
                start_time=start_time,
                end_time=end_time
            )
            messages.success(request, f"Урок '{subject.name}' добавлен в {dict(DAYS_OF_WEEK)[int(day_of_week)]}.")
        return redirect('manage_lessons')

    subgrades = SubGrade.objects.filter(grade__school=user_school).order_by('grade__number', 'letter')
    subjects = Subject.objects.filter(school=user_school).order_by('name')
    return render(request, 'school/admin/add_lesson.html', {
        'subgrades': subgrades,
        'subjects': subjects,
        'days': DAYS_OF_WEEK,
    })

# Удаление урока
@login_required
def delete_lesson(request, lesson_id):
    user_school = request.user.school_user.school
    lesson = get_object_or_404(Lesson, id=lesson_id, subgrade__grade__school=user_school)
    lesson.delete()
    messages.success(request, f"Урок '{lesson.subject.name}' удалён.")
    return redirect('manage_lessons')

from .models import News
from .forms import NewsForm

@login_required
def manage_news(request):
    user_school = request.user.school_user.school
    news_list = News.objects.filter(school=user_school).order_by('-created_at')

    if request.method == 'POST':
        form = NewsForm(request.POST, request.FILES)
        if form.is_valid():
            news = form.save(commit=False)
            news.school = user_school
            news.save()
            messages.success(request, "Новость успешно добавлена!")
            return redirect('manage_news')
    else:
        form = NewsForm()

    return render(request, 'school/admin/manage_news.html', {'news_list': news_list, 'form': form})

@login_required
def edit_news(request, news_id):
    user_school = request.user.school_user.school
    news = get_object_or_404(News, id=news_id, school=user_school)

    if request.method == 'POST':
        form = NewsForm(request.POST, request.FILES, instance=news)
        if form.is_valid():
            form.save()
            messages.success(request, "Новость успешно обновлена!")
            return redirect('manage_news')
    else:
        form = NewsForm(instance=news)

    return render(request, 'school/admin/edit_news.html', {'form': form, 'news': news})


from django.shortcuts import redirect

@login_required
def delete_news(request, news_id):
    user_school = request.user.school_user.school
    news = get_object_or_404(News, id=news_id, school=user_school)
    news.delete()
    messages.success(request, "Новость успешно удалена!")
    return redirect('manage_news')

from django.http import JsonResponse
from django.template.loader import render_to_string

@login_required
def news_detail(request, news_id):
    user_school = request.user.school_user.school
    news = get_object_or_404(News, id=news_id, school=user_school)

    if request.method == "GET":
        html = render_to_string('school/admin/news_detail.html', {'news': news}, request)
        return JsonResponse({'html': html})


@login_required
def grade_list(request):
    user_school = request.user.school_user.school
    grades = Grade.objects.filter(school=user_school).order_by('number')
    slides = Slide.objects.filter(school=user_school)
    last_slide = slides.last() 
    news = News.objects.filter(school=user_school).order_by('-created_at')
    
    return render(request, 'school/grade_list.html', {
        'grades': grades,
        'slides': [last_slide],
        'news': news,
    })

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Slide, SchoolUser
from .forms import SlideForm

@login_required
def upload(request):
    school_user = request.user.school_user
   
    if request.method == 'POST':
        form = SlideForm(request.POST, request.FILES)
        if form.is_valid():
            slide = form.save(commit=False)
            slide.school = school_user.school  # Привязка слайда к школе
            slide.save()
            return redirect('grade_list')  # Перенаправление на страницу со списком слайдов
    else:
        form = SlideForm()
    
    return render(request, 'school/admin//upload.html', {'form': form})
