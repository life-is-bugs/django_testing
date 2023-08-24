from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from ..models import Note


User = get_user_model()
CONST_SLUG = 'title-slug'


def make_urls():
    urls = {
        'test_pages_availability': [
            ('notes:home', None),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
        ],
        'test_notes_availability_for_auth_user': [
            'notes:list',
            'notes:success',
            'notes:add'
        ],
        'test_availability_for_note_detail_edit_and_delete': [
            'notes:detail',
            'notes:edit',
            'notes:delete'
        ],
        'test_redirect_for_anonymous_client': [
            ('notes:list', None),
            ('notes:success', None),
            ('notes:add', None),
            ('notes:detail', (CONST_SLUG,)),
            ('notes:edit', (CONST_SLUG,)),
            ('notes:delete', (CONST_SLUG,)),
        ]
    }
    return urls


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
        urls = make_urls()['test_pages_availability']
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                self.assertEqual(
                    self.client.get(url).status_code,
                    HTTPStatus.OK
                )

    def test_notes_availability_for_auth_user(self):
        """
        2) Аутентифицированному пользователю доступна страница со списком
           заметок notes/, страница успешного добавления заметки done/,
           страница добавления новой заметки add/.
        """
        urls = make_urls()['test_notes_availability_for_auth_user']
        self.client.force_login(self.author)
        for page in urls:
            with self.subTest(page=page):
                url = reverse(page)
                self.assertEqual(
                    self.client.get(url).status_code,
                    HTTPStatus.OK
                )

    def test_availability_for_note_detail_edit_and_delete(self):
        """
        3) Страницы отдельной заметки, удаления и редактирования
           заметки доступны только автору заметки.
           Если на эти страницы попытается зайти другой пользователь —
           вернётся ошибка 404.
        """
        test_pages = make_urls()[
            'test_availability_for_note_detail_edit_and_delete'
        ]
        user_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in user_statuses:
            self.client.force_login(user)
            for name in test_pages:
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.note.slug,))
                    self.assertEqual(
                        self.client.get(url).status_code,
                        status
                    )

    def test_redirect_for_anonymous_client(self):
        """
        4) При попытке перейти на страницу списка заметок,
           страницу успешного добавления записи, страницу добавления
           заметки, отдельной заметки, редактирования или удаления заметки
           анонимный пользователь перенаправляется на страницу логина.
        """
        login_url = reverse('users:login')
        urls = make_urls()['test_redirect_for_anonymous_client']
        for page, args in urls:
            with self.subTest(page=page):
                url = reverse(page, args=args)
                redirect_url = f'{login_url}?next={url}'
                self.assertRedirects(
                    self.client.get(url),
                    redirect_url
                )
