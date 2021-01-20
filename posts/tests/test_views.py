from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from django import forms

from posts.forms import PostForm
from posts.models import Group, Post, User


INDEX_URL = reverse('index')
NEW_URL = reverse('new_post')
AUTHOR_URL = reverse('about:author')
TECH_URL = reverse('about:tech')


class PagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username='VasiaBasov')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Описание тестовой группы',
        )

        cls.second_group = Group.objects.create(
            title='Тестовый заголовок второй',
            slug='second-slug',
            description='Описание тестовой группы',
        )

        cls.post = Post.objects.create(
            text='Тестовый тест',
            pub_date='06.01.2021',
            author=cls.user,
            group=cls.group,
        )

        cls.form = PostForm()
        cls.GROUP_URL = reverse('group', kwargs={'slug': 'test-slug'})
        cls.SECOND_GROUP_URL = reverse('group',
                                       kwargs={'slug': 'second-slug'})
        cls.USER_URL = reverse('profile', args=(cls.user.username,))
        cls.POST_URL = reverse('post', kwargs={'username': cls.user,
                                               'post_id': cls.post.id})
        cls.EDIT_AUTHOR = reverse('post_edit', args=(cls.user.username,
                                                     cls.post.id))

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_page_names = {
            'index.html': INDEX_URL,
            'new.html': NEW_URL,
            'group.html': self.GROUP_URL,
            'about/author.html': AUTHOR_URL,
            'about/tech.html': TECH_URL,
        }
        for template, reverse_name in templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_new_post_page_show_correct_context(self):
        """Шаблон new_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(NEW_URL)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_group_page_show_correct_context(self):
        """Шаблон group сформирован с правильным контекстом."""
        response = self.authorized_client.get(self.GROUP_URL)
        self.assertEqual(response.context.get('group').title,
                         'Тестовый заголовок')
        self.assertEqual(response.context.get('group').description,
                         'Описание тестовой группы')
        self.assertEqual(response.context.get('group').slug, 'test-slug')

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(INDEX_URL)
        post_text_0 = response.context.get('page')[0].text
        post_author_0 = response.context.get('page')[0].author.username
        self.assertEqual(post_text_0, 'Тестовый тест')
        self.assertEqual(post_author_0, 'VasiaBasov')

    def test_post_with_group_anailable_in_index_page(self):
        """Если при создании поста указать группу,
        то этот пост появляется на главной странице."""
        response = self.authorized_client.get(INDEX_URL)
        post_group_0 = response.context.get('page')[0].group.title
        self.assertEqual(post_group_0, 'Тестовый заголовок')

    def test_post_with_group_anailable_in_group_slug_page(self):
        """Если при создании поста указать группу,
        то этот пост появляется на странице выбранной группы."""
        response = self.authorized_client.get(self.GROUP_URL)
        post_group_0 = response.context.get('page')[0].group.title
        self.assertEqual(post_group_0, 'Тестовый заголовок')

    def test_post_not_in_group(self):
        """Тестовый пост не появился на странице second_group"""
        response = self.authorized_client.get(self.SECOND_GROUP_URL)
        self.assertEqual(len(response.context['page']), 0)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом"""
        response = self.authorized_client.get(self.USER_URL)
        expected_post = self.post
        actual_post = response.context.get('page')[0]
        self.assertEqual(actual_post, expected_post)

    def test_post_page_show_correct_context(self):
        """Шаблон post сформирован с правильным контекстом"""
        response = self.authorized_client.get(self.POST_URL)
        expected_post = self.post
        actual_post = response.context.get('post')
        self.assertEqual(actual_post, expected_post)

    def test_edit_page_show_correct_context(self):
        """Шаблон edit сформирован с правильным контекстом"""
        response = self.authorized_client.get(self.EDIT_AUTHOR)
        expected_post = self.post
        actual_post = response.context.get('post')
        self.assertEqual(actual_post, expected_post)

    def test_first_page_contains_ten_posts(self):
        """Страница содержит 10 постов"""
        for post in range(14):
            Post.objects.create(
                text=f'Такст на 14 постов {post}',
                author=get_user_model().objects.create(
                    username=f'Bloger{post}'),
            )
        response = self.authorized_client.get(INDEX_URL)
        self.assertEqual(len(response.context.get('page')), 10)

    def test_about_author_url_exists_at_desired_location(self):
        """Страница /author/ доступна любому пользователю."""
        response = self.guest_client.get(AUTHOR_URL)
        self.assertEqual(response.status_code, 200)

    def test_about_tech_url_exists_at_desired_location(self):
        """Страница /tech/ доступна любому пользователю."""
        response = self.guest_client.get(TECH_URL)
        self.assertEqual(response.status_code, 200)
