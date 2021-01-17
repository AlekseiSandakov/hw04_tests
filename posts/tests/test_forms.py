from django.test import Client, TestCase
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Group, Post, User


class CreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_author = User.objects.create_user(username='VasiaBasov')
        cls.user_other = User.objects.create_user(username='PetrBasov')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test',
            description='Описание тестовой группы'
        )

        cls.post = Post.objects.create(
            text='Тестовый тест',
            pub_date='06.01.2021',
            author=CreateFormTests.user_author,
            group=CreateFormTests.group
        )
        cls.form = PostForm()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client_VasiaBasov = Client()
        self.authorized_client_PetrBasov = Client()
        self.authorized_client_VasiaBasov.force_login(self.user_author)
        self.authorized_client_PetrBasov.force_login(self.user_other)

    def test_create_post(self):
        """Валидная форма создает запись в post."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый тест',
            'group': self.group.id,
        }
        response = self.authorized_client_VasiaBasov.post(
            reverse('new_post'),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(response, '/')
        self.assertEqual(Post.objects.count(), posts_count+1)
        self.assertTrue(Post.objects.filter(text='Тестовый тест').exists())

    def test_edit_post(self):
        """Тестируем изменение поста."""
        test_text = 'Тестовое создание поста'
        test_text_edit = 'Измененый текст для тестового поста'
        post = Post.objects.create(
            text=test_text,
            author=self.user_author,
            group=self.group,
        )
        group_havent_post = Group.objects.create(
            title='test-group-2',
            slug='test_group_2',
        )
        post_count = Post.objects.count()
        form_data = {
            'text': test_text_edit,
            'group': group_havent_post.id,
        }
        response = self.authorized_client_VasiaBasov.post(
            reverse('post_edit', args=(self.user_author.username, post.id)),
            data=form_data,
            follow=True
        )
        post_edit = Post.objects.first()
        self.assertRedirects(
            response,
            reverse('post', args=(self.user_author.username, post.id))
        )
        self.assertEqual(Post.objects.count(), post_count)
        self.assertEqual(post_edit.text, test_text_edit)
        self.assertEqual(post_edit.author, self.user_author)
        self.assertEqual(post_edit.group, group_havent_post)
