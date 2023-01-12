from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User

User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        """Создание записи в БД"""
        super().setUpClass()
        cls.test_user = User.objects.create_user(username='authorized')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.test_user,
            group=cls.group,
            text='Тестовый пост',
        )

    def setUp(self):
        self.user = User.objects.create_user(username='StasBasov')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон"""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group', kwargs={'slug': self.group.slug}): 'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': self.user.username}): 'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk}): 'posts/post_detail.html',
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }

        for reverse_name, template in templates_pages_names.items():
            """типы полей формы в словаре context соответствуют ожиданиям"""
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_context_index(self):
        """Считаем количество постов на странице"""
        response = self.authorized_client.get(reverse('posts:index'))
        page_object = response.context['page_obj']
        self.assertEqual(len(page_object), 1)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
        reverse('posts:profile',
                 kwargs={'username': PostPagesTests.test_user}))
        self.assertEqual(response.context['page_obj'][0],
                         PostPagesTests.post)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUp(cls):
        cls.user = User.objects.create_user(
            username='Author'
        )
        cls.group = Group.objects.create(title='Тестовая группа',
                                         slug='test_group',
                                         description='Тестовое описание')

        for i in range(13):
            Post.objects.create(text=f'Тестовый текст {i}',
                                group=cls.group,
                                author=cls.user)
        cls.authorizend_client = Client()
        cls.authorizend_client.force_login(cls.user)
        cls.page_name = {
            reverse('posts:index'): 'page_obj',
            reverse('posts:group', kwargs={'slug': 'testo_slug'}): 'page_obj',
            reverse('posts:profile',
                    kwargs={'username': 'testUser'}): 'page_obj',
        }

    def test_first_page_contains_ten_records(self):
        """Проверка: на второй странице должно быть три поста"""
        for value, expected in self.page_name.items():
            with self.subTest(value=value):
                response = self.client.get(reverse('posts:index'))
                self.assertEqual(len(response.context[expected]), 10)

    def test_second_page_contains_three_records(self):
        """Проверка: на второй странице должно быть три поста"""
        for value, expected in self.page_name.items():
            with self.subTest(value=value):
                response = self.client.get(reverse('posts:index') + '?page=2')
                self.assertEqual(len(response.context[expected]), 3)
