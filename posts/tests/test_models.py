from django.test import TestCase, Client

from posts.forms import PostForm
from posts.models import Group, Post, User


class ModelTest(TestCase):
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
            author=ModelTest.user_author,
            group=ModelTest.group
        )
        cls.form = PostForm()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client_VasiaBasov = Client()
        self.authorized_client_PetrBasov = Client()
        self.authorized_client_VasiaBasov.force_login(self.user_author)
        self.authorized_client_PetrBasov.force_login(self.user_other)

    def test_verbose_name_post(self):
        """verbose_name в полях совпадает с ожидаемым."""
        post = ModelTest.post
        field_verboses = {
            'text': 'Текст',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected)

    def test_verbose_name_group(self):
        """verbose_name в полях совпадает с ожидаемым."""
        group = ModelTest.group
        field_verboses = {
            'title': 'Заголовок',
            'slug': 'Адрес',
            'description': 'Описание',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).verbose_name, expected)

    def test_help_text_post(self):
        """help_text в полях совпадает с ожидаемым."""
        post = ModelTest.post
        field_help_texts = {
            'text': 'Напишите текст',
            'pub_date': 'Дата',
            'author': 'Автор поста',
            'group': 'Название группы',
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected)

    def test_help_text_group(self):
        """help_text в полях совпадает с ожидаемым."""
        group = ModelTest.group
        field_help_texts = {
            'title': 'Напишите заголовок',
            'slug': 'Адрес для страницы',
            'description': 'Описание группы',
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).help_text, expected)

    def test_object_name_is_text_fild(self):
        """В поле __str__  объекта post записано значение поля post.text."""
        post = ModelTest.post
        expected_object_name = post.text
        self.assertEqual(expected_object_name, str(post))

    def test_object_name_is_title_fild(self):
        """В поле __str__  объекта group записано значение поля group.title."""
        group = ModelTest.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))
