from django.test import TestCase, Client
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Group, Post, User


INDEX_URL = reverse('index')
NEW_URL = reverse('new_post')
SLUG = 'test'
GROUP_URL = reverse('group', args=[SLUG])


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_author = User.objects.create_user(username='VasiaBasov')
        cls.user_other = User.objects.create_user(username='PetrBasov')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test',
            description='Описание тестовой группы',
        )
        cls.post = Post.objects.create(
            text='Тестовый тест',
            pub_date='06.01.2021',
            author=cls.user_author,
            group=cls.group,
        )
        cls.form = PostForm()
        cls.EDIT_AUTHOR = reverse('post_edit',
                                  args=(cls.user_author.username,
                                        cls.post.id))
        cls.USER_URL = reverse('profile', args=(cls.user_author.username,))
        cls.AUTHOR_POST = reverse('post', args=(cls.user_author.username,
                                                cls.post.id))

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client_VasiaBasov = Client()
        self.authorized_client_PetrBasov = Client()
        self.authorized_client_VasiaBasov.force_login(self.user_author)
        self.authorized_client_PetrBasov.force_login(self.user_other)

    def test_home_url_exists_at_desired_location(self):
        """Страница / доступна любому пользователю."""
        response = self.guest_client.get(INDEX_URL)
        self.assertEqual(response.status_code, 200)

    def test_new_list_url_exists_at_desired_location(self):
        """Страница /new/ доступна авторизованному пользователю."""
        response = self.authorized_client_VasiaBasov.get(NEW_URL)
        self.assertEqual(response.status_code, 200)

    def test_group_list_url_exists_at_desired_location(self):
        """Страница /group/ доступна авторизованному пользователю."""
        response = self.authorized_client_VasiaBasov.get(GROUP_URL)
        self.assertEqual(response.status_code, 200)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            'index.html': INDEX_URL,
            'group.html': GROUP_URL,
            'new.html': NEW_URL,
            'new.html': self.EDIT_AUTHOR,
        }
        for template, reverse_name in templates_url_names.items():
            with self.subTest():
                response = self.authorized_client_VasiaBasov.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_username_list_url_exists_at_desired_location(self):
        """Страница <username> доступна авторизованному пользователю."""
        response = self.authorized_client_VasiaBasov.get(self.USER_URL)
        self.assertEqual(response.status_code, 200)

    def test_username_post_id_list_url_exists_at_desired_location(self):
        """Страница <username>/<post_id> доступна
           авторизованному пользователю."""
        response = self.authorized_client_VasiaBasov.get(self.AUTHOR_POST)
        self.assertEqual(response.status_code, 200)

    def test_post_edit_url_exists_at_desired_location(self):
        """Страница post_edit не доступна любому пользователю."""
        response = self.guest_client.get(self.EDIT_AUTHOR)
        self.assertEqual(response.status_code, 302)

    def test_auth_author_user_page_edit(self):
        """Автору поста доступно редактирование поста"""
        response = self.authorized_client_VasiaBasov.get(self.EDIT_AUTHOR)
        self.assertEqual(response.status_code, 200)

    def test_not_auth_author_user_page_edit(self):
        """Проверка редиректа авторизированного пользователя, но не автора."""
        response = self.authorized_client_PetrBasov.get(self.EDIT_AUTHOR)
        self.assertEqual(response.status_code, 302)
