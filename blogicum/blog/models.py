from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse

from core.models import PublishedModel

TITLE_LENGTH = 256
CATEGORY_LENGTH = 64
User = get_user_model()
DEFAULT_RELATED_NAMES_POSTS = 'posts'


class Post(PublishedModel):
    """Класс публикаций"""

    title = models.CharField('Заголовок', max_length=TITLE_LENGTH)
    text = models.TextField('Текст')
    pub_date = models.DateTimeField(
        'Дата и время публикации',
        help_text='Если установить дату и время в будущем — можно'
        ' делать отложенные публикации.'
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор публикации',
        related_name=DEFAULT_RELATED_NAMES_POSTS,
    )

    location = models.ForeignKey(
        'Location',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Местоположение',
        related_name=DEFAULT_RELATED_NAMES_POSTS,
    )

    category = models.ForeignKey(
        'Category',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Категория',
        related_name=DEFAULT_RELATED_NAMES_POSTS,
    )

    image = models.ImageField('Фото', upload_to='post_images', blank=True)

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ('-pub_date',)

    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={'post_id': self.id})

    def __str__(self):
        return self.title


class Category(PublishedModel):
    """Класс категории публикаций"""

    title = models.CharField('Заголовок', max_length=TITLE_LENGTH)
    description = models.TextField('Описание')
    slug = models.SlugField(
        'Идентификатор', max_length=CATEGORY_LENGTH, unique=True,
        help_text='Идентификатор страницы для URL; разрешены символы'
        ' латиницы, цифры, дефис и подчёркивание.'
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title


class Location(PublishedModel):
    """Класс локации публикаций"""

    name = models.CharField('Название места', max_length=TITLE_LENGTH)

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name


class Comment(models.Model):
    """Класс комментирования публикаций"""

    text = models.TextField('Комментарий')
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Пост')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               verbose_name='Автор')
    created_at = models.DateTimeField('Дата и время создания',
                                      auto_now_add=True)

    class Meta:
        ordering = ('created_at',)
