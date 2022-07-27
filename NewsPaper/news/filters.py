from django_filters import FilterSet, DateFilter
from django.forms.widgets import DateInput
from .models import Post


# Создаем свой набор фильтров для модели Post.
class PostFilter(FilterSet):
    date_gt = DateFilter(field_name='post_time',
                         lookup_expr='gt',
                         label='Опубликовано позже, чем',
                         widget=DateInput(attrs={'type': 'date'}))

    class Meta:
        # В Meta классе мы должны указать Django модель,
        # в которой будем фильтровать записи.
        model = Post
        # В fields мы описываем по каким полям модели
        # будет производиться фильтрация.
        fields = {
            # поиск по названию
            'header': ['icontains'],
            # поиск по имени автора (точному)
            'author': ['exact'],
        }
