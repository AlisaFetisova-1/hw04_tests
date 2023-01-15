from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User
from posts.forms import PostForm

User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        """Создание записи в БД"""
        super().setUpClass()
        cls.user = User.objects.create_user(username='authorized')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='Тестовый пост',
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон"""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group',
                    kwargs={'slug': self.group.slug}): 'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username':
                            self.user.username}): 'posts/profile.html',
            reverse('posts:post_detail',
                    kwargs={'post_id':
                            self.post.pk}): 'posts/post_detail.html',
            reverse('posts:post_edit',
                    kwargs={'post_id':
                            self.post.id}): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }

        for reverse_name, template in templates_pages_names.items():
            """типы полей формы в словаре context соответствуют ожиданиям"""
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_context_index(self):
        response = self.authorized_client.get(reverse('posts:index'))
        page_object = response.context['page_obj']
        self.assertEqual(len(page_object), 1)
        self.assertIsInstance(page_object[0], Post)

    def test_context_group_posts(self):
        response = self.authorized_client.get(
            reverse(
                'posts:group',
                kwargs={'slug': PostPagesTests.group.slug}
            )
        )
        page_object = response.context['page_obj']
        self.assertEqual(len(page_object), 1)
        self.assertIsInstance(page_object[0], Post)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'username': PostPagesTests.user}))
        self.assertEqual(response.context['page_obj'][0],
                         PostPagesTests.post)
        context_author = response.context.get('author')
        self.assertEqual(context_author, self.post.author)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}))
        post_text_0 = {response.context['post'].text: 'Тестовый пост',
                       response.context['post'].group: self.group,
                       response.context['post'].author: self.user.username}
        for value, expected in post_text_0.items():
            self.assertEqual(post_text_0[value], expected)

    def test_post_create_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = testing_pages = (
            f'/posts/{PostPagesTests.post.pk}/edit/',
             '/create/',
        )
        for url in testing_pages:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertIsInstance(
                    response.context['form'],
                    PostForm
                )
                if 'edit' in url:
                    self.assertEqual(
                        response.context['is_edit'],
                        True
                    )
                    self.assertEqual(
                        response.context['post'],
                        PostPagesTests.post
                    )

    def test_paginator(self):
        bulk_posts = []
        for i in range(12):
            bulk_posts.append(Post(
                text=f'Тестовый пост {i}',
                author=PostPagesTests.user,
                group=PostPagesTests.group)
            )
            Post.objects.bulk_create(bulk_posts)

        reverse_name_posts = [
            reverse('posts:index'),
            reverse('posts:profile',
                    kwargs={'username': f'{self.user.username}'}),
            reverse('posts:group',
                    kwargs={'slug': f'{self.group.slug}'}),
        ]

        for reverse_name in reverse_name_posts:
            with self.subTest(reverse_name=reverse_name):
                response = self.client.get(reverse_name)
                self.assertEqual(
                    len(response.context['page_obj']), 10,
                    'Количество постов на первой странице не равно десяти'
                )
