from django.utils.text import Truncator
from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        verbose_name='Заголовок',
        max_length=200,
        help_text='Напишите заголовок'
    )
    slug = models.SlugField(
        verbose_name='Адрес',
        unique=True,
        help_text='Адрес для страницы'
    )
    description = models.TextField(
        verbose_name='Описание',
        help_text='Описание группы'
    )

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(
        verbose_name='Текст',
        help_text='Напишите текст'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
        help_text='Дата'
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name="posts",
        help_text='Автор поста'
    )
    group = models.ForeignKey(
        Group,
        verbose_name='Группа',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="group",
        help_text='Название группы'
    )
    objects = models.Manager()

    class Meta:
        ordering = ('-pub_date',)

    def __str__(self):
        self.text = Truncator(self.text).words(10)
        return self.text
