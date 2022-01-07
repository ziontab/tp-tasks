import django
from django import forms

from django.forms import ModelForm, TextInput, PasswordInput, DateTimeInput, Textarea, FileInput
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from app.models import *
from django.forms import PasswordInput
from django.contrib.auth.password_validation import validate_password
from django.core import validators
from django import forms


class LoginForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password']
        widgets = {
            'username': TextInput(
                attrs={'class': 'form-control',
                       'maxlength': 100,
                       'placeholder': 'My_NiCkNaMe55',
                       'required': True,
                       'id': 'username-input',
                       'required pattern': '^[-a-zA-Z0-9_+.@]+$'}),
            'password': PasswordInput(
                attrs={'class': 'form-control',
                       'maxlength': 100,
                       'placeholder': 'My_NiCkNaMe55',
                       'required': True,
                       'id': 'password-input',
                       'required pattern': '^(?=.*\d)(?=.*[A-Z]).{8,}$',
                       })
        }

        labels = {
            'username': 'Login',
            'password': 'Password'
        }

    def clean(self):
        pass


class SignupForm(forms.ModelForm):
    repeat_password = forms.CharField(required=True,
                                      widget=PasswordInput(attrs={
                                          'type': 'password',
                                          'class': 'form-control',
                                          'maxlength': 100,
                                          'placeholder': 'My_NiCkNaMe55',
                                          'id': 'repeat-password-input',
                                          'required pattern': '^(?=.*\d)(?=.*[A-Z]).{8,}$',
                                      }),
                                      label='Password check')

    # TODO: use Imageform
    avatar = forms.FileField(required=True,
                             widget=FileInput(attrs={
                                 'class': 'form-control',
                                 'id': 'avatar-input',
                                 'type': 'file',
                                 'name': 'avatar',
                                 'accept': 'image/*',
                             }),
                             label='Avatar')

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

        widgets = {
            'username': TextInput(
                attrs={'class': 'form-control',
                       'maxlength': 100,
                       'placeholder': 'My_NiCkNaMe55',
                       'required': True,
                       'id': 'username-input',
                       'required pattern': '^[-a-zA-Z0-9_+.@]+$'}),
            'password': PasswordInput(
                attrs={'class': 'form-control',
                       'maxlength': 100,
                       'type': 'password',
                       'placeholder': 'My_NiCkNaMe55',
                       'required': True,
                       'id': 'password-input',
                       'required pattern': '^(?=.*\d)(?=.*[A-Z]).{8,}$'}),
            'email': TextInput(attrs={
                'class': 'form-control',
                'maxlength': 100,
                'required': True,
                'id': 'email-input',
                'placeholder': 'name@example.com',
                'type': 'email',
            }),
        }

        labels = {
            'username': 'Login',
            'password': 'Password',
            'email': 'Email',
        }

    def clean(self):
        pass

    def clean_username(self):
        if User.objects.filter(username=self.cleaned_data['username']).exists():
            # self.add_error('username', 'This username is already in use')
            raise forms.ValidationError('This username is already in use')
        return self.cleaned_data['username']

    def clean_email(self):
        if User.objects.filter(email=self.cleaned_data['email']).exists():
            # self.add_error('email', 'This email is already in use')
            raise forms.ValidationError('This email is already in use')
        return self.cleaned_data['email']

    def clean_repeat_password(self):
        password = self.cleaned_data['password']
        repeat_password = self.cleaned_data['repeat_password']
        if not password or not repeat_password:
            return password
        if password != repeat_password:
            self.add_error('repeat_password', 'Passwords do not match!')
            return ""

        try:
            django.contrib.auth.password_validation.validate_password(password)
        except forms.ValidationError as error:
            self.add_error('password', 'Invalid password. it must contain one upper and one lowercase letter and at '
                                       'least one number and be 8-100 characters long')
            return ""
        return password

    def save(self, **kwargs):
        username = self.cleaned_data['username']
        email = self.cleaned_data['email']
        password = self.cleaned_data['password']
        user = User.objects.create_user(username, email, password)

        profile = Profile.objects.create(user_id=user)
        if self.cleaned_data['avatar'] is not None:
            profile.avatar = self.cleaned_data['avatar']
            profile.save()

        return user


class SettingsForm(forms.Form):
    repeat_password = forms.CharField(required=False,
                                      widget=PasswordInput(attrs={
                                          'type': 'password',
                                          'class': 'form-control',
                                          'maxlength': 100,
                                          'placeholder': 'My_NiCkNaMe55',
                                          'id': 'repeat-password-input',
                                          # 'required pattern': '(^\s{0,}$)|(^.a$)|()',
                                      }),
                                      label='Password check',
                                      )

    username = forms.CharField(required=False,
                               widget=TextInput(
                                   attrs={'class': 'form-control',
                                          'maxlength': 100,
                                          'placeholder': 'My_NiCkNaMe55',
                                          'required': False,
                                          'id': 'username-input',
                                          'value': '{{ user.username }}',
                                          'required pattern': '^[-a-zA-Z0-9_+.@]+$',
                                          }),
                               label='Login'
                               )
    email = forms.EmailField(required=False,
                             widget=TextInput(attrs={
                                 'class': 'form-control',
                                 'maxlength': 100,
                                 'required': False,
                                 'id': 'email-input',
                                 'placeholder': 'name@example.com',
                                 'type': 'email',
                                 'value': '{{user.email}}',
                             }),
                             label='Email',
                             )

    password = forms.CharField(required=False,
                               widget=PasswordInput(attrs={
                                   'type': 'password',
                                   'class': 'form-control',
                                   'maxlength': 100,
                                   'placeholder': 'My_NiCkNaMe55',
                                   'id': 'password-input',
                                   'required pattern': '(^a$)|(^$)|($)|(^)|(^b$)',
                                   # 'required pattern': '^((?=.*\d)(?=.*[A-Z]).{8,}){0,1}$',
                               }),
                               label='Password check')

    avatar = forms.FileField(required=False,
                             widget=FileInput(attrs={
                                 'class': 'form-control',
                                 'id': 'avatar-input',
                                 'type': 'file',
                                 'name': 'avatar',
                                 'accept': 'image/*',
                             }),
                             label='Avatar')

    def __init__(self, user=None, **kwargs):
        self.user = user
        super(SettingsForm, self).__init__(**kwargs)

    def clean_username(self):
        if not self.cleaned_data['username']:
            return self.cleaned_data['username']
        if self.user.username != self.cleaned_data['username']:
            if User.objects.filter(username=self.cleaned_data['username']).exists():
                self.add_error(None, 'This username is already in use')
                raise forms.ValidationError('This username is already in use')
        return self.cleaned_data['username']

    def clean_email(self):
        if not self.cleaned_data['email']:
            return self.user.email
        if self.user.email != self.cleaned_data['email']:
            if User.objects.filter(email=self.cleaned_data['email']).exists():
                self.add_error(None, 'This email is already in use')
                raise forms.ValidationError('This email is already in use')
        return self.cleaned_data['email']

    def clean_password(self):
        password = self.cleaned_data['password']
        repeat_password = self.cleaned_data['repeat_password']
        if not password or not repeat_password:
            return password
        if password != repeat_password:
            self.add_error('repeat_password', 'Passwords do not match!')
            return ""

        try:
            django.contrib.auth.password_validation.validate_password(password)
        except forms.ValidationError as error:
            self.add_error('password', 'Invalid password. it must contain one upper and one lowercase letter and at '
                                       'least one number and be 8-100 characters long')
            return ""
        return password

    def save(self, **kwargs):
        self.user.username = self.cleaned_data['username']
        self.user.email = self.cleaned_data['email']

        if self.cleaned_data['password']:
            self.user.set_password(self.cleaned_data['password'])

        self.user.save()

        profile = Profile.objects.get(user_id=self.user)
        if self.cleaned_data['avatar'] is not None:
            profile.avatar = self.cleaned_data['avatar']
            profile.save()

        return self.user

# class ImageForm(forms.ModelForm):
#     class Meta:
#         model = Profile
#         fields = ['avatar']
#
#         labels = {
#             'avatar': 'Upload avatar',
#         }
#
# #
# class AskForm(forms.ModelForm):
#     tags = forms.CharField(required=False,
#                            widget=forms.TextInput(attrs={
#                                'class': 'form-control',
#                            }),
#                            label='Tags')
#
#     class Meta:
#         model = Question
#         fields = ['title', 'text']
#
#         widgets = {
#             'title': TextInput(attrs={
#                 'class': 'form-control',
#             }),
#             'text': Textarea(attrs={
#                 'class': 'form-control',
#                 'rows': '7',
#             }),
#         }
#
#         labels = {
#             'title': 'Title',
#             'text': 'Text',
#         }
#
#     def __init__(self, author=None, **kwargs):
#         self._author = author
#         super(AskForm, self).__init__(**kwargs)
#
#     def clean_tags(self):
#         self.tags = self.cleaned_data['tags'].split()
#         if len(self.tags) > 3:
#             self.add_error(None, 'use no more than 3 tags!')
#             raise forms.ValidationError('use no more than 3 tags!')
#         return self.tags
#
#     def save(self, **kwargs):
#         post = Question()
#         post.profile_id = self._author
#         post.title = self.cleaned_data['title']
#         post.text = self.cleaned_data['text']
#         post.save()
#
#         for tag in self.tags:
#             if not Tag.objects.filter(tag=tag).exists():
#                 Tag.objects.create(tag=tag)
#         post.tags.set(Tag.objects.create_question(self.tags))
#
#         return post
