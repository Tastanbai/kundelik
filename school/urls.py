from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.grade_list, name='grade_list'),       
    path('upload/', views.upload, name='upload'),  # Add the 'upload' URL pattern             # Главная страница - список классов
    path('register/', views.user_register, name='user_register'),
    path('login/', views.user_login_view, name='user_login'),
    path('logout/', views.user_logout_view, name='user_logout'),
    path('grade/<int:grade_id>/', views.subgrade_list, name='subgrade_list'),  # Подклассы для выбранного класса
    path('subgrade_list/<int:grade_id>/', views.subgrade_list, name='subgrade_list'),
    path('lesson_schedule/<int:subgrade_id>/', views.lesson_schedule, name='lesson_schedule'),


    # Кастомная админ-панель
    path('custom_admin/', views.custom_admin_dashboard, name='custom_admin_dashboard'),
    path('custom_admin/subjects/', views.manage_subjects, name='manage_subjects'),
    path('custom_admin/subgrades/', views.manage_subgrades, name='manage_subgrades'),
    path('custom_admin/lessons/', views.manage_lessons, name='manage_lessons'),
    
    # Дополнительные URL для добавления/редактирования
    path('custom_admin/subjects/add/', views.add_subject, name='add_subject'),
    path('custom_admin/subjects/delete/<int:subject_id>/', views.delete_subject, name='delete_subject'),
    
    path('custom_admin/subgrades/add/', views.add_subgrade, name='add_subgrade'),
    path('custom_admin/subgrades/delete/<int:subgrade_id>/', views.delete_subgrade, name='delete_subgrade'),
    
    path('custom_admin/lessons/add/', views.add_lesson, name='add_lesson'),
    path('custom_admin/lessons/delete/<int:lesson_id>/', views.delete_lesson, name='delete_lesson'),
    path('manage_news/', views.manage_news, name='manage_news'),
    path('edit_news/<int:news_id>/', views.edit_news, name='edit_news'),
    path('delete_news/<int:news_id>/', views.delete_news, name='delete_news'),
    path('news_detail/<int:news_id>/', views.news_detail, name='news_detail'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
