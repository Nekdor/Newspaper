from django import forms
from django.core.exceptions import ValidationError
from allauth.account.forms import SignupForm
from django.contrib.auth.models import Group

from .models import Post


# Класс формы для создания публикации (как новости, так и статьи)
class PostForm(forms.ModelForm):
    text = forms.CharField(min_length=20)

    class Meta:
        model = Post
        fields = ['author', 'header', 'category', 'text']

    def clean(self):
        cleaned_data = super().clean()
        text = cleaned_data.get('text')
        header = cleaned_data.get('header')
        if text == header:
            raise ValidationError('Текст публикации не должен совпадать с ее названием!')

        return cleaned_data


# Класс формы для редактирования новостей
# Наследуется от класса формы создания публикаций
# Добовляется проверка, что работа идет с публикацией типа "новость"
class NewsUpdateForm(PostForm):
    valid_type = 'n'

    def clean(self):
        if self.instance.type != self.valid_type:
            raise ValidationError('Тип публикации не соответствует адресу!')

        super().clean()


# Класс формы для редактирования статей
# Наследуется от класса формы редактирования новостей
# Допустимый тип меняется на "статью"
class ArticleUpdateForm(NewsUpdateForm):
    valid_type = 'a'


# Класс формы для удаления новости
# Сама форма не содержит полей
# Нужна для проверки правильности типа публикации
class NewsDeleteForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = []

    valid_type = 'n'

    def clean(self):
        if self.instance.type != self.valid_type:
            raise ValidationError('Тип публикации не соответствует адресу!')

        super().clean()


# Класс формы для удаления статьи
# Наследуется от класса формы для удаления новости
# Допустимый тип меняется на "статью"
class ArticleDeleteForm(NewsDeleteForm):
    valid_type = 'a'


class BasicSignupForm(SignupForm):

    def save(self, request):
        user = super(BasicSignupForm, self).save(request)
        common_group = Group.objects.get(name='common')
        common_group.user_set.add(user)
        return user

