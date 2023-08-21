from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from ..models import Note


User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='author')
        cls.reader = User.objects.create(username='reader')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='title-slug',
            author=cls.author,
        )

    def test_pages_availability(self):
        """
        1) Главная страница доступна анонимному пользователю.
        5) Страницы регистрации пользователей, входа в учётную запись
           и выхода из неё доступны всем пользователям.
        """
        urls = (
            ('notes:home', None),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_notes_availability_for_auth_user(self):
        """
        2) Аутентифицированному пользователю доступна страница со списком
           заметок notes/, страница успешного добавления заметки done/,
           страница добавления новой заметки add/.
        """
        urls = (
            'notes:list',
            'notes:success',
            'notes:add',
        )
        self.client.force_login(self.author)
        for page in urls:
            with self.subTest(page=page):
                url = reverse(page)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_note_detail_edit_and_delete(self):
        """
        3) Страницы отдельной заметки, удаления и редактирования
           заметки доступны только автору заметки.
           Если на эти страницы попытается зайти другой пользователь —
           вернётся ошибка 404.
        """
        user_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        test_pages = [
            'notes:detail',
            'notes:edit',
            'notes:delete'
        ]
        for user, status in user_statuses:
            self.client.force_login(user)
            for name in test_pages:
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        """
        4) При попытке перейти на страницу списка заметок,
           страницу успешного добавления записи, страницу добавления
           заметки, отдельной заметки, редактирования или удаления заметки
           анонимный пользователь перенаправляется на страницу логина.
        """
        login_url = reverse('users:login')
        urls = (
            ('notes:list', None),
            ('notes:success', None),
            ('notes:add', None),
            ('notes:detail', (self.note.slug,)),
            ('notes:edit', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
        )
        for page, args in urls:
            with self.subTest(page=page):
                url = reverse(page, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
