from django.contrib import admin
from .models import Post, Category, Author


# функция обнуления рейтинга публикации
def nullify_rating(modeladmin, request, queryset):
    for post in queryset:
        post.nullify()


# функция увеличения рейтинга публикации
def like(modeladmin, request, queryset):
    for post in queryset:
        post.like()


# функция уменьшения рейтинга публикации
def dislike(modeladmin, request, queryset):
    for post in queryset:
        post.dislike()


# функция обновления рейтинга автора
def update_rating(modeladmin, request, queryset):
    for author in queryset:
        author.update_rating()


# описания для более понятного представления действий в админ панели
nullify_rating.short_description = 'Обнулить рейтинг'
like.short_description = 'Увеличить рейтинг'
dislike.short_description = 'Уменьшить рейтинг'
update_rating.short_description = 'Обновить рейтинг'


# создаём новый класс для представления публикаций в админке
class PostAdmin(admin.ModelAdmin):
    list_display = ("header", "preview", "author", "type", "post_time", "rating")  # кортеж имён полей для отображения
    list_filter = ("author", "type", "category")  # кортеж имён полей для фильтрации
    search_fields = ("header", "text", "author__user__username")  # кортеж имён полей для поиска
    actions = [nullify_rating, like, dislike]  # добавляем действия в список


# создаём новый класс для представления категорий в админке
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)  # кортеж имён полей для отображения
    search_fields = ("name",)  # кортеж имён полей для поиска


# создаём новый класс для представления авторов в админке
class AuthorAdmin(admin.ModelAdmin):
    list_display = ("user", "rating")  # кортеж имён полей для отображения
    search_fields = ("user__username",)  # кортеж имён полей для поиска
    actions = [update_rating]  # добавляем действия в список


admin.site.register(Post, PostAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Author, AuthorAdmin)

