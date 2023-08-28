from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from ..models import Note
from ..forms import NoteForm


User = get_user_model()

NOTES_BASE_URL = 'notes:'
USERS_BASE_URL = 'users:'

USERS_LOGIN_URL = reverse(f'{USERS_BASE_URL}login')
USERS_LOGOUT_URL = reverse(f'{USERS_BASE_URL}logout')
USERS_SIGNUP_URL = reverse(f'{USERS_BASE_URL}signup')
NOTES_HOME_URL = reverse(f'{NOTES_BASE_URL}home')
NOTES_LIST_URL = reverse(f'{NOTES_BASE_URL}list')
NOTES_SUCCESS_URL = reverse(f'{NOTES_BASE_URL}success')
NOTES_ADD_URL = reverse(f'{NOTES_BASE_URL}add')
NOTES_DETAIL_URL = reverse(f'{NOTES_BASE_URL}detail', args=('slug', ))
NOTES_EDIT_URL = reverse(f'{NOTES_BASE_URL}edit', args=('slug', ))
NOTES_DELETE_URL = reverse(f'{NOTES_BASE_URL}delete', args=('slug', ))
NOTES_LIST_REDIRECT_URL = f'{USERS_LOGIN_URL}?next={NOTES_LIST_URL}'
NOTES_SUCCESS_REDIRECT_URL = f'{USERS_LOGIN_URL}?next={NOTES_SUCCESS_URL}'
NOTES_ADD_REDIRECT_URL = f'{USERS_LOGIN_URL}?next={NOTES_ADD_URL}'
NOTES_DETAIL_REDIRECT_URL = f'{USERS_LOGIN_URL}?next={NOTES_DETAIL_URL}'
NOTES_EDIT_REDIRECT_URL = f'{USERS_LOGIN_URL}?next={NOTES_EDIT_URL}'
NOTES_DELETE_REDIRECT_URL = f'{USERS_LOGIN_URL}?next={NOTES_DELETE_URL}'


class TestContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Создаем записи в БД без сохранения
        cls.reader = User.objects.create(username='reader')
        cls.author = User.objects.create(username='author')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='slug',
            author=cls.author,
        )
        cls.reader_client, cls.author_client = Client(), Client()
        cls.reader_client.force_login(cls.reader)
        cls.author_client.force_login(cls.author)

    def test_note_in_user_notes_list(self):
        with self.subTest(user=self.author.username, note=self.note):
            response = self.author_client.get(NOTES_LIST_URL)
            resp_note = response.context['object_list'].filter(
                id=self.note.pk).first()
            self.assertEqual(resp_note, self.note)
            self.assertEqual(resp_note.title, self.note.title)
            self.assertEqual(resp_note.text, self.note.text)
            self.assertEqual(resp_note.slug, self.note.slug)
            self.assertEqual(resp_note.author, self.note.author)

    def test_note_not_in_user_notes_list(self):
        with self.subTest(user=self.reader, note=self.note):
            response = self.reader_client.get(NOTES_LIST_URL)
            resp_note = response.context['object_list'].filter(
                id=self.note.pk).exists()
            self.assertEqual(resp_note, False)

    def test_pages_contains_form(self):
        urls = (
            NOTES_ADD_URL,
            NOTES_EDIT_URL,
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                response_form = response.context.get('form')
                self.assertIsInstance(response_form, NoteForm)
