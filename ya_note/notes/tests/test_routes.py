from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from ..models import Note


User = get_user_model()

CONST_SLUG = 'slug'
NOTES_BASE_URL = 'notes:'
USERS_BASE_URL = 'users:'

OK = HTTPStatus.OK
NOT_FOUND = HTTPStatus.NOT_FOUND

USERS_LOGIN_URL = reverse(f'{USERS_BASE_URL}login')
USERS_LOGOUT_URL = reverse(f'{USERS_BASE_URL}logout')
USERS_SIGNUP_URL = reverse(f'{USERS_BASE_URL}signup')
NOTES_HOME_URL = reverse(f'{NOTES_BASE_URL}home')
NOTES_LIST_URL = reverse(f'{NOTES_BASE_URL}list')
NOTES_SUCCESS_URL = reverse(f'{NOTES_BASE_URL}success')
NOTES_ADD_URL = reverse(f'{NOTES_BASE_URL}add')
NOTES_DETAIL_URL = reverse(f'{NOTES_BASE_URL}detail', args=(CONST_SLUG, ))
NOTES_EDIT_URL = reverse(f'{NOTES_BASE_URL}edit', args=(CONST_SLUG, ))
NOTES_DELETE_URL = reverse(f'{NOTES_BASE_URL}delete', args=(CONST_SLUG, ))

NOTES_LIST_REDIRECT_URL = f'{USERS_LOGIN_URL}?next={NOTES_LIST_URL}'
NOTES_SUCCESS_REDIRECT_URL = f'{USERS_LOGIN_URL}?next={NOTES_SUCCESS_URL}'
NOTES_ADD_REDIRECT_URL = f'{USERS_LOGIN_URL}?next={NOTES_ADD_URL}'
NOTES_DETAIL_REDIRECT_URL = f'{USERS_LOGIN_URL}?next={NOTES_DETAIL_URL}'
NOTES_EDIT_REDIRECT_URL = f'{USERS_LOGIN_URL}?next={NOTES_EDIT_URL}'
NOTES_DELETE_REDIRECT_URL = f'{USERS_LOGIN_URL}?next={NOTES_DELETE_URL}'


class TestRoutes(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.anon = User.objects.create(username='anon')
        cls.reader = User.objects.create(username='reader')
        cls.author = User.objects.create(username='author')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='slug',
            author=cls.author,
        )
        (
            cls.anon_client,
            cls.reader_client,
            cls.author_client
        ) = Client(), Client(), Client()

        cls.reader_client.force_login(cls.reader)
        cls.author_client.force_login(cls.author)

    def test_response_codes(self):
        data = (
            (NOTES_HOME_URL, self.anon_client, OK),
            (USERS_LOGIN_URL, self.anon_client, OK),
            (USERS_LOGOUT_URL, self.anon_client, OK),
            (USERS_SIGNUP_URL, self.anon_client, OK),
            (NOTES_LIST_URL, self.reader_client, OK),
            (NOTES_SUCCESS_URL, self.reader_client, OK),
            (NOTES_ADD_URL, self.reader_client, OK),
            (NOTES_DETAIL_URL, self.author_client, OK),
            (NOTES_EDIT_URL, self.author_client, OK),
            (NOTES_DELETE_URL, self.author_client, OK),
            (NOTES_DETAIL_URL, self.reader_client, NOT_FOUND),
            (NOTES_EDIT_URL, self.reader_client, NOT_FOUND),
            (NOTES_DELETE_URL, self.reader_client, NOT_FOUND),
        )
        for url, client, status in data:
            with self.subTest(url=url, client=client, status=status):
                response = client.get(url)
                self.assertEqual(response.status_code, status)

    def test_redirects(self):
        data = (
            (NOTES_LIST_URL, NOTES_LIST_REDIRECT_URL),
            (NOTES_SUCCESS_URL, NOTES_SUCCESS_REDIRECT_URL),
            (NOTES_ADD_URL, NOTES_ADD_REDIRECT_URL),
            (NOTES_DETAIL_URL, NOTES_DETAIL_REDIRECT_URL),
            (NOTES_EDIT_URL, NOTES_EDIT_REDIRECT_URL),
            (NOTES_DELETE_URL, NOTES_DELETE_REDIRECT_URL)
        )
        for url, redirect in data:
            with self.subTest(user=self.anon, url=url):
                self.assertRedirects(self.anon_client.get(url), redirect)
