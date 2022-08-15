from django.db.models.signals import m2m_changed
from django.dispatch import receiver  # импортируем нужный декоратор
from .models import Post, Category, CategorySubscriber
from .tasks import notify_subscribers


# Сигнал для оповещения подпищеков
@receiver(m2m_changed, sender=Post.category.through)
def notify_subscribers_signal(sender, instance, pk_set, action, **kwargs):
    # Функция должна срабатывать только если событием, вызвавшим сигнал, было окончание сохранения объекта.
    if action == 'post_add':
        # Вызываем задачу рассылки. Передается не сама публикация, а ее ключ, тк аргумент должен быть json-сериализуем
        notify_subscribers.apply_async([instance.id, *pk_set])



