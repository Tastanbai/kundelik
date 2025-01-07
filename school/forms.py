# school/forms.py
from django import forms
from django.contrib.auth.models import User

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Подтверждение пароля', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name')
        labels = {
            'username': 'Имя пользователя',
            'first_name': 'Фамилия',
            'email': 'Почта'
        }

        help_texts = {
            'username': None,  # Убираем стандартное сообщение
        }

    def clean_password2(self):
        cd = self.cleaned_data
        if cd.get('password') != cd.get('password2'):
            raise forms.ValidationError('Пароли не совпадают.')
        return cd

class LoginForm(forms.Form):
    username = forms.CharField(label="Имя пользователя")
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput)

# forms.py
class PowerPointUploadForm(forms.Form):
    title = forms.CharField(max_length=255)
    file = forms.FileField(help_text='Выберите PowerPoint файл')


from django import forms
from .models import News

class NewsForm(forms.ModelForm):
    class Meta:
        model = News
        fields = ['title', 'content', 'images']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 5}),
        }
