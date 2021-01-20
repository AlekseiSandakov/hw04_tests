from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User


NEW_URL = reverse('new_post')


class CreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='VasiaBasov')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test',
            description='Описание тестовой группы',
        )
        cls.post = Post.objects.create(
            text='Тестовый тест',
            pub_date='06.01.2021',
            author=cls.user,
            group=cls.group,
        )
        cls.EDIT_URLS = reverse('post_edit', args=(cls.user.username,
                                                   cls.post.id))

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_new_post(self):
        """При отправке формы создаётся новая запись в базе данных."""
        counter = 1
        form_data = {
            'text': 'Тестовый текст',
            'group': self.group.id
        }
        self.authorized_client.post(NEW_URL, data=form_data, follow=True)
        self.assertEqual(Post.objects.count(), counter + 1)

    def test_edit_post(self):
        """Тестируем изменение поста."""
        group_havent_post = Group.objects.create(
            title='test-group-2',
            slug='test_group_2',
        )
        post_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
            'group': group_havent_post.id,
        }
        self.authorized_client.post(self.EDIT_URLS,
                                    data=form_data,
                                    follow=True)
        post_edit = Post.objects.first()
        self.assertEqual(Post.objects.count(), post_count)
        self.assertEqual(post_edit.text, form_data['text'])
        self.assertEqual(post_edit.author, self.user)
        self.assertEqual(post_edit.group, group_havent_post)
