from django.core.management.base import BaseCommand, CommandError
from ...models import Post, Category


class Command(BaseCommand):

    help = 'Удаляет все публикации в определенной категории'
    requires_migrations_checks = True  # напоминать ли о миграциях

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('argument', nargs='+', type=str)

    def handle(self, *args, **options):

        category_set = {Category.objects.get(name=name) for name in options['argument']}

        self.stdout.readable()
        # спрашиваем пользователя, действительно ли он хочет удалить все публикации данных категорий
        self.stdout.write('Do you really want to delete posts of categories' + str(options['argument']) + '? yes/no')
        answer = input()  # считываем подтверждение

        if answer == 'yes':  # в случае подтверждения действительно удаляем публикации
            Post.objects.filter(category__in=category_set).delete()
            self.stdout.write(self.style.SUCCESS('Succesfully wiped posts!'))
            return

        self.stdout.write(
            self.style.ERROR('Deletion cancelled'))  # в случае неправильного подтверждения, сообщаем об отмене