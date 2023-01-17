from http import HTTPStatus
from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from posts.models import Post, Group

User = get_user_model()


class PostFormTests(TestCase):

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='auth')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.group = Group.objects.create(title='Тестовая группа',
                                          slug='test-group',
                                          description='Описание')

    def test_create_post(self):
        '''Валидная форма создает новую запись в базе данных'''
        posts_count = Post.objects.count()
        form_data = {'text': 'Текст записанный в форму',
                     'group': self.group.id,
                     #'image': '',
                     }
        response = self.authorized_client.post(reverse('posts:post_create'),
                                               data=form_data,
                                               follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(Post.objects.filter(
                        text=form_data["text"],
                        group=self.group.id,
                        author=self.user
                        ).exists())
        self.assertEqual(Post.objects.count(),
                         posts_count + 1,
                         )
        #self.assertNotEqual(Post.objects.first().image==form_data['image'],
        # 'Пользователь не может изменить image поста')

    #def test_show_image_index(self):
        #response = self.authorized_client.post(число чего-то??)
        #self.assertEqual(response.context['post'],self.post)
    def test_edit_post(self):
        """ Валидная форма изменяет запись в Пост"""
        self.post = Post.objects.create(text='Тестовый текст',
                                        author=self.user,
                                        group=self.group)
        old_text = self.post
        self.group2 = Group.objects.create(title='Тестовая группа2',
                                           slug='tests-group',
                                           description='Описание')
        form_data = {'text': 'Текст записанный в форму',
                     'group': self.group2.id}
        posts_count = Post.objects.count()
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': old_text.id}),
            data=form_data,
            follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(Post.objects.filter(
                        group=self.group2.id,
                        author=self.user,
                        pub_date=self.post.pub_date
                        ).exists())
        self.assertNotEqual(old_text.text, form_data['text'])
        self.assertNotEqual(old_text.group, form_data['group'])
        self.assertEqual(Post.objects.count(), posts_count,
                         'Число постов не должно меняться'
                         'при редактировании поста')
