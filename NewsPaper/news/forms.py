from django import forms
from django.core.exceptions import ValidationError
from allauth.account.forms import SignupForm
from django.contrib.auth.models import Group
from .models import Post, CategorySubscriber
from datetime import datetime, time


# Класс формы для создания публикации (как новости, так и статьи)
class PostForm(forms.ModelForm):
    text = forms.CharField(min_length=20)

    def __init__(self, *args, **kwargs):
        """ Добавляем автора публикации в конструктор класса"""
        self.author = kwargs.pop('author')
        super().__init__(*args, **kwargs)

    class Meta:
        model = Post
        fields = ['header', 'category', 'text']

    def clean(self):
        cleaned_data = super().clean()
        text = cleaned_data.get('text')
        header = cleaned_data.get('header')
        if text == header:
            raise ValidationError('Текст публикации не должен совпадать с ее названием!')
        midnight = datetime.combine(datetime.today(), time.min)
        posts_today = Post.objects.filter(author=self.author, post_time__gt=midnight)
        if posts_today.count() >= 3:
            raise ValidationError('Вы больше не можете создавать публикации сегодня!')
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


#  Класс формы для подписки на категорию
class SubscribeForm(forms.ModelForm):
    class Meta:
        model = CategorySubscriber
        fields = ['category']

    def __init__(self, *args, **kwargs):
        """ Добавляем запрос в конструктор класса"""
        self.request = kwargs.pop('request')
        super().__init__(*args, **kwargs)

    def clean(self):
        """Метод верификации формы дополняется проверкой отсутствия подписки"""
        cleaned_data = super().clean()
        # Выбранная категория
        cat = cleaned_data.get('category')
        # Текущий пользователь
        sub = self.request.user
        # Проверка, нет ли уже подписки на выбранную категорию у текущего пользователя
        if self.Meta.model.objects.filter(category=cat, subscriber=sub).exists():
            raise ValidationError('Вы уже подписаны на данную категорию!')
        return cleaned_data
