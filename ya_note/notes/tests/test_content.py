from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from ..models import Note
from ..forms import NoteForm


User = get_user_model()

CONST_SLUG = 'slug'
NOTES_BASE_URL = 'notes:'
USERS_BASE_URL = 'users:'

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

        # Сохраем сессии клиентов, авторизуемся
        cls.reader_client, cls.author_client = Client(), Client()
        cls.reader_client.force_login(cls.reader)
        cls.author_client.force_login(cls.author)

    def test_note_in_user_notes_list(self):
        """
        1) Отдельная заметка передаётся на страницу со списком
        заметок в списке object_list в словаре context;
        """

        response = self.author_client.get(NOTES_LIST_URL)
        # Изменение имени переменной
        response_note = response.context['object_list'].filter(
            id=self.note.pk)
        # Контроль существования заметки на странице
        self.assertTrue(response_note.exists())

        response_note = response_note.first()

        self.assertEqual(response_note, self.note)
        self.assertEqual(response_note.title, self.note.title)
        self.assertEqual(response_note.text, self.note.text)
        self.assertEqual(response_note.slug, self.note.slug)
        self.assertEqual(response_note.author, self.note.author)

    def test_note_not_in_user_notes_list(self):
        response = self.reader_client.get(NOTES_LIST_URL)

        # Изменение имени переменной с resp_note
        # Атрибут класса note имеет тип Note, следовательно, является заметкой
        # Для демонстрации:
        self.assertIsInstance(self.note, Note)
        response_note = response.context['object_list'].filter(
            id=self.note.pk).exists()

        # Исходя из того, что проверка выше валидна,
        # нет смысла менять проверку ниже
        self.assertFalse(response_note)

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
