from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from django import forms

from posts.forms import PostForm
from posts.models import Group, Post, User


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
            description='Описание тестовой группы'
        )

        cls.second_group = Group.objects.create(
            title='Тестовый заголовок второй',
            slug='second-slug',
            description='Описание тестовой группы'
        )

        cls.post = Post.objects.create(
            text='Тестовый тест',
            pub_date='06.01.2021',
            author=PagesTests.user,
            group=PagesTests.group
        )

        cls.form = PostForm()

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_page_names = {
            'index.html': reverse('index'),
            'new.html': reverse('new_post'),
            'group.html': (reverse('group', kwargs={'slug': 'test-slug'})),
            'about/author.html': '/about/author/',
            'about/tech.html': '/about/tech/',
        }
        for template, reverse_name in templates_page_names.items():
            with self.subTest(template=template):
                response = PagesTests.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_new_post_page_show_correct_context(self):
        """Шаблон new_post сформирован с правильным контекстом."""
        response = PagesTests.authorized_client.get(reverse('new_post'))
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
        response = PagesTests.authorized_client.get(
            reverse('group', kwargs={'slug': 'test-slug'})
        )
        self.assertEqual(response.context.get('group').title,
                         'Тестовый заголовок')
        self.assertEqual(response.context.get('group').description,
                         'Описание тестовой группы')
        self.assertEqual(response.context.get('group').slug, 'test-slug')

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = PagesTests.authorized_client.get(reverse('index'))
        post_text_0 = response.context.get('page')[0].text
        post_author_0 = response.context.get('page')[0].author.username
        self.assertEqual(post_text_0, 'Тестовый тест')
        self.assertEqual(post_author_0, 'VasiaBasov')

    def test_post_with_group_anailable_in_index_page(self):
        """Если при создании поста указать группу,
        то этот пост появляется на главной странице."""
        response = self.authorized_client.get(reverse('index'))
        post_group_0 = response.context.get('page')[0].group.title
        self.assertEqual(post_group_0, 'Тестовый заголовок')

    def test_post_with_group_anailable_in_group_slug_page(self):
        """Если при создании поста указать группу,
        то этот пост появляется на странице выбранной группы."""
        response = self.authorized_client.get(
            reverse('group', kwargs={'slug': 'test-slug'})
        )
        post_group_0 = response.context.get('page')[0].group.title
        self.assertEqual(post_group_0, 'Тестовый заголовок')

    def test_post_not_in_group(self):
        """Тестовый пост не появился на странице second_group"""
        response = self.authorized_client.get(
            reverse('group', kwargs={'slug': self.second_group.slug})
        )
        self.assertEqual(len(response.context['page']), 0)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом"""
        response = PagesTests.authorized_client.get(
            reverse('profile', kwargs={'username': 'VasiaBasov'}))
        expected_post = PagesTests.post
        actual_post = response.context.get('page')[0]
        self.assertEqual(actual_post, expected_post)

    def test_post_page_show_correct_context(self):
        """Шаблон post сформирован с правильным контекстом"""
        response = self.authorized_client.get(
            reverse('post', kwargs={'username': PagesTests.user,
                    'post_id': PagesTests.post.id}))
        expected_post = PagesTests.post
        actual_post = response.context.get('post')
        self.assertEqual(actual_post, expected_post)

    def test_edit_page_show_correct_context(self):
        """Шаблон edit сформирован с правильным контекстом"""
        response = self.authorized_client.get(
            reverse('post_edit', kwargs={'username': PagesTests.user,
                    'post_id': PagesTests.post.id}))
        expected_post = PagesTests.post
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
        response = PagesTests.authorized_client.get(reverse('index'))
        self.assertEqual(len(response.context.get('page')), 10)

    def test_about_author_url_exists_at_desired_location(self):
        """Страница /author/ доступна любому пользователю."""
        response = self.guest_client.get('/about/author/')
        self.assertEqual(response.status_code, 200)

    def test_about_tech_url_exists_at_desired_location(self):
        """Страница /tech/ доступна любому пользователю."""
        response = self.guest_client.get('/about/tech/')
        self.assertEqual(response.status_code, 200)
