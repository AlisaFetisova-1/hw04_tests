from django.contrib.auth import get_user_model
from django.db import models


User = get_user_model()


class Group(models.Model):
    """класс Group наследник класса Model с описанием моделей и их типов """
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()

    def __str__(self) -> str:
        return self.title


class Post(models.Model):
    """класс Post наследник класса Model с описанием моделей и их типов """
    text = models.TextField(
        'Текст поста',
        help_text='Введите текст поста'
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True
    )
    author = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='posts'
        )
    group = models.ForeignKey(Group, blank=True,
                              null=True,
                              on_delete=models.SET_NULL,
                              related_name='posts',
                              verbose_name='Группа',
                              help_text='Выберите группу'
                            )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    def __str__(self) -> str:
        return self.text[:15]

    class Meta:
        ordering = ["-pub_date", ]
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

