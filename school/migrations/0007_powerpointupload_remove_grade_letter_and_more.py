# Generated by Django 5.0.6 on 2024-12-24 11:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('school', '0006_alter_grade_number'),
    ]

    operations = [
        migrations.CreateModel(
            name='PowerPointUpload',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('file', models.FileField(upload_to='powerpoints/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='grade',
            name='letter',
        ),
        migrations.AlterField(
            model_name='grade',
            name='number',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='lesson',
            name='day_of_week',
            field=models.IntegerField(choices=[(1, 'Понедельник'), (2, 'Вторник'), (3, 'Среда'), (4, 'Четверг'), (5, 'Пятница'), (6, 'Суббота')]),
        ),
    ]