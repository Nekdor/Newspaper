from django.urls import path
# Импортируем созданные нами представления
from .views import PostsList, PostDetail, FilteredPostsList, NewsCreate, NewsUpdate, NewsDelete, SubscriptionCreate


urlpatterns = [
    # path — означает путь.
    # Т.к. наше объявленное представление является классом,
    # а Django ожидает функцию, нам надо представить этот класс в виде view.
    # Для этого вызываем метод as_view.
    path('', PostsList.as_view(), name='post_list'),
    # pk — это первичный ключ публикации, который будет выводиться у нас в шаблон
    # int — указывает на то, что принимаются только целочисленные значения
    path('<int:pk>/', PostDetail.as_view(), name='post_detail'),
    path('search/', FilteredPostsList.as_view(), name='post_search'),
    path('create/', NewsCreate.as_view(), name='news_create'),
    path('<int:pk>/update/', NewsUpdate.as_view(), name='news_update'),
    path('<int:pk>/delete/', NewsDelete.as_view(), name='news_delete'),
    path('subscribe/', SubscriptionCreate.as_view(), name='subscribe')
]
