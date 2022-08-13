import os

from django.db.models.signals import m2m_changed
from django.dispatch import receiver  # импортируем нужный декоратор
from .models import Post, Category, CategorySubscriber, PostCategory
from django.core.mail import EmailMultiAlternatives  # импортируем класс для создание объекта письма с html
from django.template.loader import render_to_string  # импортируем функцию, которая срендерит наш html в текст


# Сигнал для оповещения подпищеков
@receiver(m2m_changed, sender=Post.category.through)
def notify_subscribers(sender, instance, pk_set, action, **kwargs):
    # Функция должна срабатывать только если событием, вызвавшим сигнал, было окончание сохранения объекта.
    if action == 'post_add':
        # Первичный ключ публикации
        post_pk = instance.pk
        # Ссылка на публикацию
        link = f'http://127.0.0.1:8000/news/{post_pk}/'
        # Список всех категорий публикации
        category_set = {Category.objects.get(pk=pk) for pk in pk_set}
        # Проходимся по всем подпискам на категории новой публикации
        for subscription in CategorySubscriber.objects.filter(category__in=category_set):
            # Поиск подписок на категории публикации
            # юзер
            user = subscription.subscriber
            # юзернейм
            username = user.username
            # почта юзера
            to_email = user.email
            # название категории
            category_name = subscription.category.name
            # Заголовок письма
            subject = f'Новая публикация: {instance.header}'
            # получаем наш html
            html_content = render_to_string(
                'new_post.html',
                {
                    'post': instance,
                    'username': username,
                    'link': link,
                    'category_name': category_name
                }
            )

            msg = EmailMultiAlternatives(
                # В тему письма выносим заголовок публикации
                subject=subject,
                # Сообщение пользователю
                body=f'Здравствуй, {username}. Новая статья в твоём любимом разделе {category_name}!',
                from_email=str(os.getenv('EMAIL_HOST_USER')) + '@yandex.ru',  # почта, с которой отправляем письмо
                to=[to_email]  # почта получателя
            )
            msg.attach_alternative(html_content, "text/html")  # добавляем html

            msg.send()  # отсылаем

