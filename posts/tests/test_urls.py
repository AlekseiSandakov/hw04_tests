from django.test import TestCase, Client
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Group, Post, User


class StaticURLTests(TestCase):
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
            author=StaticURLTests.user_author,
            group=StaticURLTests.group
        )
        cls.form = PostForm()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client_VasiaBasov = Client()
        self.authorized_client_PetrBasov = Client()
        self.authorized_client_VasiaBasov.force_login(self.user_author)
        self.authorized_client_PetrBasov.force_login(self.user_other)

    def test_home_url_exists_at_desired_location(self):
        """Страница / доступна любому пользователю."""
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_new_list_url_exists_at_desired_location(self):
        """Страница /new/ доступна авторизованному пользователю."""
        response = self.authorized_client_VasiaBasov.get('/new/')
        self.assertEqual(response.status_code, 200)

    def test_group_list_url_exists_at_desired_location(self):
        """Страница /group/ доступна авторизованному пользователю."""
        response = self.authorized_client_VasiaBasov.get('/group/test/')
        self.assertEqual(response.status_code, 200)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            'index.html': '/',
            'group.html': '/group/test/',
            'new.html': '/new/',
            'new.html': '/VasiaBasov/1/edit/',
        }
        for template, reverse_name in templates_url_names.items():
            with self.subTest():
                response = self.authorized_client_VasiaBasov.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_username_list_url_exists_at_desired_location(self):
        """Страница <username> доступна авторизованному пользователю."""
        response = self.authorized_client_VasiaBasov.get('/VasiaBasov/')
        self.assertEqual(response.status_code, 200)

    def test_username_post_id_list_url_exists_at_desired_location(self):
        """Страница <username>/<post_id> доступна
           авторизованному пользователю."""
        response = self.authorized_client_VasiaBasov.get('/VasiaBasov/1/')
        self.assertEqual(response.status_code, 200)

    def test_post_edit_url_exists_at_desired_location(self):
        """Страница post_edit не доступна любому пользователю."""
        response = self.guest_client.get('post_edit')
        self.assertEqual(response.status_code, 404)

    def test_auth_author_user_page_edit(self):
        """Автору поста доступно редактирование поста"""
        response = self.authorized_client_VasiaBasov.get(reverse(
            "post_edit", args=[StaticURLTests.user_author.username,
                               StaticURLTests.post.id]))
        self.assertEqual(response.status_code, 200)

    def test_not_auth_author_user_page_edit(self):
        """Авторизированному не автору поста не
           доступно редактирование поста"""
        response = self.authorized_client_PetrBasov.get(reverse(
            "post_edit", args=[StaticURLTests.user_other.username,
                               StaticURLTests.post.id]))
        self.assertEqual(response.status_code, 404)

    def test_new_post_authorized_not_author(self):
        """Проверка редиректа авторизированного пользователя, но не автора."""
        reverse_name_url = {
            reverse('post_edit', args=(StaticURLTests.user_author,
                                       StaticURLTests.post.id)):
            reverse('post', args=(StaticURLTests.user_author,
                                  StaticURLTests.post.id)),
        }
        for reverse_name, url in reverse_name_url.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client_PetrBasov.get(reverse_name,
                                                                follow=True)
                self.assertRedirects(response, url, 302)
