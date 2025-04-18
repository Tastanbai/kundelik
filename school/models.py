# school/models.py
import os
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User

DAYS_OF_WEEK = [
    (1, 'Понедельник'),
    (2, 'Вторник'),
    (3, 'Среда'),
    (4, 'Четверг'),
    (5, 'Пятница'),
    (6, 'Суббота'),
]


# models.py
class School(models.Model):
    name = models.CharField(max_length=255, unique=True)

class SchoolUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='school_user')
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='users')

    class Meta:
        verbose_name = "Пользователь школы"
        verbose_name_plural = "Пользователи школы"

    def __str__(self):
        return f"{self.user.username} - {self.school.name}"

class Grade(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='grades')
    number = models.PositiveIntegerField(null=True)

    class Meta:
        verbose_name = "Класс"
        verbose_name_plural = "Классы"

    def __str__(self):
        return f"{self.number}"

class SubGrade(models.Model):
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, related_name='subgrades')
    letter = models.CharField(max_length=1)  # Например, 'А', 'Б', 'В' и т.д.

    class Meta:
        verbose_name = "Подкласс"
        verbose_name_plural = "Подклассы"
        unique_together = (('grade', 'letter'),)


    def __str__(self):
        return f"{self.grade.number}{self.letter}"

class Subject(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='subjects')
    name = models.CharField(max_length=50)

    class Meta:
        verbose_name = "Предмет"
        verbose_name_plural = "Предметы"
        unique_together = (('school', 'name'),)

    def __str__(self):
        return self.name

class Lesson(models.Model):
    subgrade = models.ForeignKey(SubGrade, on_delete=models.CASCADE, related_name='lessons')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    day_of_week = models.IntegerField(choices=DAYS_OF_WEEK)
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"
        ordering = ['day_of_week', 'start_time']

    def __str__(self):
        return f"{self.subgrade} - {self.subject} ({self.get_day_of_week_display()})"


class News(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='news')
    title = models.CharField(max_length=255)
    content = models.TextField()
    images = models.ImageField(upload_to='news_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Новость"
        verbose_name_plural = "Новости"

    def __str__(self):
        return self.title

class Slide(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='slides')
    title = models.CharField(max_length=255, verbose_name="Название презентации")
    pdf_file = models.FileField(upload_to='slides/', verbose_name="PDF файл")

    def __str__(self):
        return self.title
