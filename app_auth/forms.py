from django import forms
from app_auth.models import CustomUser, Profile
from legacy.models import WebUsers

class LoginForm(forms.Form):
    username = forms.CharField(max_length=100, label="Username")
    password = forms.CharField(widget=forms.PasswordInput, label="Password")

class RegistrationForm(forms.Form):
    username = forms.CharField(max_length=100, label="Логин", required=True)
    email = forms.EmailField(label="Почта", required=True)
    password = forms.CharField(widget=forms.PasswordInput, label="Пароль", required=True)
    password_confirm = forms.CharField(widget=forms.PasswordInput, label="Подтверждение пароля", required=True)

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if CustomUser.objects.filter(username=username).exists():
            raise forms.ValidationError('Пользователь с таким логином уже существует')
        return username

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError('Пароли не совпадают')
        if WebUsers.objects.filter(web_username=cleaned_data.get('username')).exists():
            raise forms.ValidationError('Пользователь с таким логином уже существует')
        return cleaned_data


class ProfileModelForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['phone', 'address', 'first_name', 'last_name', 'patronymic_name','cdek_address', 'telegram_id']
        labels = {
            'phone': 'Телефон',
            'address': 'Адрес',
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'patronymic_name': 'Отчество',
            'cdek_address': 'Адрес CDEK',
            'telegram_id': 'Telegram ID'
        }


class RecoveryPasswordForm(forms.Form):
    email = forms.EmailField(label="Почта вашей учетной записи:", required=True)
    token = forms.CharField(widget=forms.HiddenInput(), required=False)  # Скрытое поле для токена

class RecoveryPasswordFormChangePasswordForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput, label="Пароль", required=True)
    password_confirm = forms.CharField(widget=forms.PasswordInput, label="Подтверждение пароля", required=True)
    token = forms.CharField(widget=forms.HiddenInput(), required=False)

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError('Пароли не совпадают')
        return cleaned_data



class CallbackResponseForm(forms.Form):
    email = forms.EmailField(label="Почта", required=True)
    connect = forms.CharField(label="Укажите предпочтительный способ связи", required=False)
    name = forms.CharField(label="Имя", required=False)
    message = forms.CharField(label="Что случилось?", widget=forms.Textarea, required=True)