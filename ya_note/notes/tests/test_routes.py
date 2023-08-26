from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from ..models import Note


User = get_user_model()
NOTES_BASE_URL = 'notes:'
USERS_BASE_URL = 'users:'

# Расчёт урлов на уровне модуля нецелесообразен,
# т.к. меняются аргументы (80 строка, notes).


class TestRoutes(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Заполнение БД без сохранения.
        Выполняется раз за весь тест модуля.
        """

        # Создаем записи в БД без сохранения
        cls.anon = User.objects.create(username='anon')
        cls.reader = User.objects.create(username='reader')
        cls.author = User.objects.create(username='author')

        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='title-slug',
            author=cls.author,
        )
        (
            cls.anon_client,
            cls.reader_client,
            cls.author_client
        ) = Client(), Client(), Client()
        cls.reader_client.force_login(cls.reader)
        cls.author_client.force_login(cls.author)

    def test_pages_status_code(self):
        """
        Проверка кодов возвратов.
        """
        data = (
            (f'{NOTES_BASE_URL}home', self.anon,
             self.anon_client, HTTPStatus.OK),
            (f'{USERS_BASE_URL}login', self.anon,
             self.anon_client, HTTPStatus.OK),
            (f'{USERS_BASE_URL}logout', self.anon,
             self.anon_client, HTTPStatus.OK),
            (f'{USERS_BASE_URL}signup', self.anon,
             self.anon_client, HTTPStatus.OK),
            (f'{NOTES_BASE_URL}list', self.reader,
             self.reader_client, HTTPStatus.OK),
            (f'{NOTES_BASE_URL}success', self.reader,
             self.reader_client, HTTPStatus.OK),
            (f'{NOTES_BASE_URL}add', self.reader,
             self.reader_client, HTTPStatus.OK),
            (f'{NOTES_BASE_URL}detail', self.author,
             self.author_client, HTTPStatus.OK),
            (f'{NOTES_BASE_URL}edit', self.author,
             self.author_client, HTTPStatus.OK),
            (f'{NOTES_BASE_URL}delete', self.author,
             self.author_client, HTTPStatus.OK),
            (f'{NOTES_BASE_URL}detail', self.reader,
             self.reader_client, HTTPStatus.NOT_FOUND),
            (f'{NOTES_BASE_URL}edit', self.reader,
             self.reader_client, HTTPStatus.NOT_FOUND),
            (f'{NOTES_BASE_URL}delete', self.reader,
             self.reader_client, HTTPStatus.NOT_FOUND),
        )

        for page, user, client, status in data:

            with self.subTest(user=user, page=page):

                if page.split(':')[1] in ('detail', 'edit', 'delete'):
                    args = (self.note.slug, )
                else:
                    args = None

                url = reverse(page, args=args)
                response = client.get(url)

                self.assertEqual(response.status_code, status)

    def test_redirects(self):
        """
        Проверка перенаправлений.
        """
        pages = (
            f'{NOTES_BASE_URL}list',
            f'{NOTES_BASE_URL}success',
            f'{NOTES_BASE_URL}add',
            f'{NOTES_BASE_URL}detail',
            f'{NOTES_BASE_URL}edit',
            f'{NOTES_BASE_URL}delete',
        )
        login_url = reverse(f'{USERS_BASE_URL}login')
        for page in pages:
            with self.subTest(user=self.anon, page=page):
                if page.split(':')[1] in ('detail', 'edit', 'delete'):
                    args = (self.note.slug, )
                else:
                    args = None
                url = reverse(page, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.anon_client.get(url)
                self.assertRedirects(response, redirect_url)
