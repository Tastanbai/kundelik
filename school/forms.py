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


from django import forms
from .models import News

class NewsForm(forms.ModelForm):
    class Meta:
        model = News
        fields = ['title', 'content', 'images']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 5}),
        }



from django import forms
from .models import Slide

class SlideForm(forms.ModelForm):
    class Meta:
        model = Slide
        fields = ['title', 'pdf_file']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите название презентации',
            }),
            'pdf_file': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'application/pdf',
            }),
        }

