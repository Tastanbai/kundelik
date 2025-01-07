# school/views.py

import os
from django.dispatch import receiver
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.contrib import messages
from pptx import Presentation

from mysite import settings

from .forms import PowerPointUploadForm, UserRegistrationForm, LoginForm
from .models import PowerPointSlide, SchoolUser, School, Grade, SubGrade, Subject, Lesson

DAYS_OF_WEEK = [
    (1, 'Понедельник'),
    (2, 'Вторник'),
    (3, 'Среда'),
    (4, 'Четверг'),
    (5, 'Пятница'),
    (6, 'Суббота'),
]

# Регистрация пользователя
# views.py
# views.py
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

# Главная страница - список классов

# # views.py
# @login_required
# def grade_list(request):
#     user_school = request.user.school_user.school
#     grades = Grade.objects.filter(school=user_school).order_by('number')
#     return render(request, 'school/grade_list.html', {'grades': grades})

# Список подклассов для выбранного класса
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

# Добавление урока (опционально)
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

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import os
from pdf2image import convert_from_path
from pptx import Presentation
import win32com.client
import pythoncom
import tempfile

# @login_required
# def upload(request):
#     if request.method == 'POST':
#         form = PowerPointUploadForm(request.POST, request.FILES)
#         if form.is_valid():
#             try:
#                 uploaded_file = request.FILES['file']
#                 max_file_size = 10 * 1024 * 1024  # 10 МБ
                
#                 # Проверка размера файла
#                 if uploaded_file.size > max_file_size:
#                     messages.error(request, 'Файл слишком большой. Максимальный размер — 10 МБ.')
#                     return redirect('upload')

#                 title = form.cleaned_data['title']
                
#                 # Create temp and slides directories
#                 temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp')
#                 slides_dir = os.path.join(settings.MEDIA_ROOT, 'slides')
#                 os.makedirs(temp_dir, exist_ok=True)
#                 os.makedirs(slides_dir, exist_ok=True)
                
#                 # Save uploaded PPTX
#                 pptx_path = os.path.join(temp_dir, uploaded_file.name)
#                 pdf_path = os.path.join(temp_dir, 'presentation.pdf')
                
#                 with open(pptx_path, 'wb+') as destination:
#                     for chunk in uploaded_file.chunks():
#                         destination.write(chunk)
                
#                 try:
#                     # Convert PPTX to PDF
#                     pythoncom.CoInitialize()
#                     powerpoint = win32com.client.Dispatch("Powerpoint.Application")
#                     deck = powerpoint.Presentations.Open(pptx_path)
#                     deck.SaveAs(pdf_path, 32)  # 32 is the PDF format code
#                     deck.Close()
#                     powerpoint.Quit()
#                 finally:
#                     pythoncom.CoUninitialize()
                
#                 # Convert PDF to images
#                 images = convert_from_path(pdf_path)
                
#                 # Delete existing slides
#                 PowerPointSlide.objects.all().delete()
                
#                 # Save each image
#                 for i, image in enumerate(images, start=1):
#                     image_path = f'slides/slide_{i}.jpg'
#                     full_image_path = os.path.join(settings.MEDIA_ROOT, image_path)
                    
#                     # Save with higher quality
#                     image.save(full_image_path, 'JPEG', quality=95)
                    
#                     # Create database entry
#                     PowerPointSlide.objects.create(
#                         title=f"{title} - Слайд {i}",
#                         slide=image_path,
#                         order=i-1
#                     )
                
#                 # Cleanup temporary files
#                 if os.path.exists(pptx_path):
#                     os.remove(pptx_path)
#                 if os.path.exists(pdf_path):
#                     os.remove(pdf_path)
                    
#                 messages.success(request, 'Презентация успешно загружена')
#                 return redirect('grade_list')
                
#             except Exception as e:
#                 messages.error(request, f'Ошибка при обработке презентации: {str(e)}')
#                 return redirect('upload')
#     else:
#         form = PowerPointUploadForm()
    
#     return render(request, 'school/admin/upload.html', {'form': form})

# @login_required
# def grade_list(request):
#     user_school = request.user.school_user.school
#     grades = Grade.objects.filter(school=user_school).order_by('number')
#     slides = PowerPointSlide.objects.all().order_by('order')
#     return render(request, 'school/grade_list.html', {
#         'grades': grades,
#         'slides': slides
#     })

# views.py

@login_required
def upload(request):
    if request.method == 'POST':
        form = PowerPointUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                uploaded_file = request.FILES['file']
                max_file_size = 10 * 1024 * 1024  # 10 МБ
                
                if uploaded_file.size > max_file_size:
                    messages.error(request, 'Файл слишком большой. Максимальный размер — 10 МБ.')
                    return redirect('upload')

                title = form.cleaned_data['title']
                user_school = request.user.school_user.school
                
                # Create directories if they don't exist
                school_slides_dir = os.path.join(settings.MEDIA_ROOT, 'slides', str(user_school.id))
                temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp')
                os.makedirs(school_slides_dir, exist_ok=True)
                os.makedirs(temp_dir, exist_ok=True)
                
                pptx_path = os.path.join(temp_dir, uploaded_file.name)
                pdf_path = os.path.join(temp_dir, f'presentation_{user_school.id}.pdf')
                
                with open(pptx_path, 'wb+') as destination:
                    for chunk in uploaded_file.chunks():
                        destination.write(chunk)
                
                try:
                    pythoncom.CoInitialize()
                    powerpoint = win32com.client.Dispatch("Powerpoint.Application")
                    deck = powerpoint.Presentations.Open(pptx_path)
                    deck.SaveAs(pdf_path, 32)
                    deck.Close()
                    powerpoint.Quit()
                finally:
                    pythoncom.CoUninitialize()
                
                images = convert_from_path(pdf_path)
                
                # Delete existing slides for this school only
                PowerPointSlide.objects.filter(school=user_school).delete()
                
                # Save slides in school-specific directory
                for i, image in enumerate(images, start=1):
                    image_path = f'slides/{user_school.id}/slide_{i}.jpg'
                    full_image_path = os.path.join(settings.MEDIA_ROOT, image_path)
                    
                    image.save(full_image_path, 'JPEG', quality=95)
                    
                    PowerPointSlide.objects.create(
                        title=f"{title} - Слайд {i}",
                        slide=image_path,
                        order=i-1,
                        school=user_school
                    )
                
                # Cleanup temporary files
                if os.path.exists(pptx_path):
                    os.remove(pptx_path)
                if os.path.exists(pdf_path):
                    os.remove(pdf_path)
                    
                messages.success(request, 'Презентация успешно загружена')
                return redirect('grade_list')
                
            except Exception as e:
                messages.error(request, f'Ошибка при обработке презентации: {str(e)}')
                return redirect('upload')
    else:
        form = PowerPointUploadForm()
    
    return render(request, 'school/admin/upload.html', {'form': form})

@login_required
def grade_list(request):
    user_school = request.user.school_user.school
    grades = Grade.objects.filter(school=user_school).order_by('number')
    # Only get slides for the current user's school
    slides = PowerPointSlide.objects.filter(school=user_school).order_by('order')
    news = News.objects.filter(school=user_school).order_by('-created_at')
    return render(request, 'school/grade_list.html', {
        'grades': grades,
        'slides': slides,
        'news': news,
    })

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
