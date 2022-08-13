import logging, os

from django.conf import settings
from datetime import datetime, timedelta
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from ...models import Post, CategorySubscriber, Category
from django.utils import timesince
from django.template.loader import render_to_string  # импортируем функцию, которая срендерит наш html в текст
from django.core.mail import EmailMultiAlternatives  # импортируем класс для создание объекта письма с html

logger = logging.getLogger(__name__)


# наша задача по выводу текста на экран
def my_job():
    #  Получаем значение времени неделю назад
    allowed_datetime = datetime.now() - timedelta(minutes=1)
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


# функция, которая будет удалять неактуальные задачи
def delete_old_job_executions(max_age=604_800):
    """This job deletes all apscheduler job executions older than `max_age` from the database."""
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = "Runs apscheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        # добавляем работу нашему задачнику
        scheduler.add_job(
            my_job,
            trigger=CronTrigger(minute="*/1"),
            # То же, что и интервал, но задача тригера таким образом более понятна django
            id="my_job",  # уникальный айди
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job 'my_job'.")

        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week="mon", hour="00", minute="00"
            ),
            # Каждую неделю будут удаляться старые задачи, которые либо не удалось выполнить,
            # либо уже выполнять не надо.
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info(
            "Added weekly job: 'delete_old_job_executions'."
        )

        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")