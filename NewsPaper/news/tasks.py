import os
from celery import shared_task
from .models import Post, Category, CategorySubscriber
from datetime import datetime, timedelta
from django.core.mail import EmailMultiAlternatives  # импортируем класс для создание объекта письма с html
from django.template.loader import render_to_string  # импортируем функцию, которая срендерит наш html в текст


@shared_task
def notify_subscribers(post_pk, *pk_set):
    # Восстанавливаем публикацию по первичному ключу
    instance = Post.objects.get(pk=post_pk)
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


@shared_task
def send_digest():
    #  Получаем значение времени неделю назад
    allowed_datetime = datetime.now() - timedelta(weeks=1)
    for category in Category.objects.all():
        # Отбираем подходящие публикации
        new_post_set = Post.objects.filter(category=category, post_time__gt=allowed_datetime)
        if new_post_set:
            # название категории
            category_name = category.name
            # Заголовок письма
            subject = f'Недельный дайджест категории: {category_name}'
            for subscription in CategorySubscriber.objects.filter(category=category):
                # юзер
                user = subscription.subscriber
                # юзернейм
                username = user.username
                # почта юзера
                to_email = user.email
                # получаем наш html
                html_content = render_to_string(
                    'new_posts_list.html',
                    {
                        'new_post_set': new_post_set,
                        'username': username,
                        'category_name': category_name
                    }
                )

                msg = EmailMultiAlternatives(
                    # В тему письма выносим заголовок публикации
                    subject=subject,
                    # Сообщение пользователю
                    body=f'Здравствуй, {username}!'
                         f' За прошедшую неделю категория {{ category_name }} пополнилась новыми публикациями!',
                    from_email=str(os.getenv('EMAIL_HOST_USER')) + '@yandex.ru',  # почта, с которой отправляем письмо
                    to=[to_email]  # почта получателя
                )
                msg.attach_alternative(html_content, "text/html")  # добавляем html

                msg.send()  # отсылаем