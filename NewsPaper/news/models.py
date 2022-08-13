from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class Author(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)

    def update_rating(self):
        result = 0
        for pst in Post.objects.filter(author__pk=self.pk):
            result += 3 * pst.rating
            for c in Comment.objects.filter(post__pk=pst.pk):
                result += c.rating
        for cmnt in Comment.objects.filter(author__pk=self.user.pk):
            result += cmnt.rating
        self.rating = result
        self.save()

    def __str__(self):
        return self.user.username.title()


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    subscriber = models.ManyToManyField(User, through='CategorySubscriber')

    def __str__(self):
        return self.name.title()


class Post(models.Model):

    news = 'n'
    article = 'a'
    TYPES = [(news, 'Новость'), (article, 'Статья')]

    author = models.ForeignKey(Author, on_delete=models.CASCADE, blank=True)
    type = models.CharField(max_length=1, choices=TYPES, default=news)
    post_time = models.DateTimeField(auto_now_add=True)
    category = models.ManyToManyField(Category, through='PostCategory')
    header = models.CharField(max_length=100, blank=True)
    text = models.TextField(blank=True)
    _rating = models.IntegerField(default=0, db_column='rating')

    def get_absolute_url(self):
        return reverse('post_detail', args=[str(self.id)])

    @property
    def rating(self):
        return self._rating

    def like(self):
        self._rating += 1
        self.save()

    def dislike(self):
        self._rating -= 1
        self.save()

    @property
    def preview(self):
        return str(self.text)[:124] + '...'


class PostCategory(models.Model):

    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)


class Comment(models.Model):

    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(blank=True)
    post_time = models.DateTimeField(auto_now_add=True)
    _rating = models.IntegerField(default=0, db_column='rating')

    @property
    def rating(self):
        return self._rating

    def like(self):
        self._rating += 1
        self.save()

    def dislike(self):
        self._rating -= 1
        self.save()


class CategorySubscriber(models.Model):

    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    subscriber = models.ForeignKey(User, on_delete=models.CASCADE)

    def get_absolute_url(self):
        return reverse('subscribe')
