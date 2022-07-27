from django.urls import reverse_lazy
# Импортируем класс, который говорит нам о том,
# что в этом представлении мы будем выводить список объектов из БД
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views.generic.edit import ModelFormMixin
from .models import Post
from .forms import PostForm, NewsUpdateForm, ArticleUpdateForm, NewsDeleteForm, ArticleDeleteForm
from .filters import PostFilter


class PostsList(ListView):
    # Указываем модель, объекты которой мы будем выводить
    model = Post
    # Поле, которое будет использоваться для сортировки объектов
    ordering = 'post_time'
    # Указываем имя шаблона, в котором будут все инструкции о том,
    # как именно пользователю должны быть показаны наши объекты
    template_name = 'posts.html'
    # Это имя списка, в котором будут лежать все объекты.
    # Его надо указать, чтобы обратиться к списку объектов в html-шаблоне.
    context_object_name = 'posts'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Добавляем в контекст объект фильтрации.
        context['filterset'] = self.filterset
        return context

    # Переопределяем функцию получения списка публикаций
    def get_queryset(self):
        # Получаем обычный запрос
        queryset = super().get_queryset()
        # Используем наш класс фильтрации.
        # self.request.GET содержит объект QueryDict.
        # Сохраняем нашу фильтрацию в объекте класса,
        # чтобы потом добавить в контекст и использовать в шаблоне.
        self.filterset = PostFilter(self.request.GET, queryset)
        # Возвращаем из функции отфильтрованный список публикаций
        return self.filterset.qs


class FilteredPostsList(PostsList):
    # Метод get_context_data позволяет нам изменить набор данных,
    # который будет передан в шаблон.
    template_name = 'filtered_posts.html'


class PostDetail(DetailView):
    # Модель всё та же, но мы хотим получать информацию по отдельной публикации
    model = Post
    # Используем другой шаблон — post.html
    template_name = 'post.html'
    # Название объекта, в котором будет выбранная пользователем публикация
    context_object_name = 'post'


# Добавляем представление для создания новостей.
# В используемой модели по умолчанию тип публикации - новость.
class NewsCreate(CreateView):
    # Указываем нашу разработанную форму
    form_class = PostForm
    # модель публкации
    model = Post
    # и новый шаблон, в котором используется форма.
    template_name = 'post_edit.html'


# Класс создания статей
# наследуется от класса создания новостей
# но тип принудительно меняется на статью
class ArticleCreate(NewsCreate):
    def form_valid(self, form):
        post = form.save(commit=False)
        post.type = 'a'
        return super().form_valid(form)


# Добавляем представление для редактирования новостей.
class NewsUpdate(UpdateView):
    # Указываем нашу разработанную форму
    form_class = NewsUpdateForm
    # модель публкации
    model = Post
    # и новый шаблон, в котором используется форма.
    template_name = 'post_edit.html'


# Класс редактирования статей
# наследуется от класса редактирования новостей
# но с другой формой
class ArticleUpdate(NewsUpdate):
    # Указываем нашу разработанную форму
    form_class = ArticleUpdateForm


# Представление удаляющее новость.
class NewsDelete(DeleteView):
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('post_list')
    context_object_name = 'post'
    form_class = NewsDeleteForm

    # Метод получения словаря атрибутов для работы с формой, не связанной с моделью, переопределяется.
    # В него добавляется получение объекта публикации и передача его в атрибут "instance" словаря
    # чтобы форма могла получить объект из базы данных для проверки типа публикации
    def get_form_kwargs(self):
        """Return the keyword arguments for instantiating the form."""
        kwargs = super().get_form_kwargs()
        obj = self.get_object()
        kwargs.update({"instance": obj})
        return kwargs


# Представление удаляющее статью.
# наследуется от представления, удаляющего новость
# но с другой формой
class ArticleDelete(NewsDelete):
    form_class = ArticleDeleteForm
