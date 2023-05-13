from django import forms
from django.forms import ModelForm, Textarea
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext, gettext_lazy as _
from django.contrib.auth import password_validation


class ChangeInfoForm(forms.Form):
    info = forms.CharField(label='О себе',
                           max_length=500, min_length=1)


class ChangePasswordForm(forms.Form):
    old_pass = forms.CharField(
        label='Старый пароль',
        max_length=500,
        min_length=1,
        widget=forms.PasswordInput
    )
    new_pass = forms.CharField(
        label='Новый пароль',
        max_length=500,
        min_length=1,
        widget=forms.PasswordInput
    )
    new_pass_rep = forms.CharField(
        label='Повторите новый пароль',
        max_length=500,
        min_length=1,
        widget=forms.PasswordInput
    )


class RegisterForm(UserCreationForm):
    """
    Документация по UserCreationForm, её полям, классам и функциям:
    https://docs.djangoproject.com/en/1.8/_modules/django/contrib/auth/forms/
    https://docs.djangoproject.com/en/3.0/topics/auth/default/#django.contrib.auth.forms.UserCreationForm
    """
    email = forms.EmailField(max_length=150)

    error_messages = {
        'password_mismatch': _('Введённые вами пароли не совпадают.'),
    }

    password1 = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),

    )
    password2 = forms.CharField(
        label=_("Password confirmation"),
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        strip=False,
        help_text=_("Enter the same password as before, for verification."),
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class UploadAvatarForm(forms.Form):
    image = forms.ImageField()


class TaskCreationsForm(forms.Form):
    name = forms.SlugField(max_length=200, min_length=1)
    description = forms.CharField(widget=Textarea(), max_length=1000)


class CommentForm(forms.Form):
    comment_text = forms.CharField()
