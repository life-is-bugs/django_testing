from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from ..models import Note
from ..forms import NoteForm


User = get_user_model()
BASE_URL = 'notes:'

# Расчёт урлов на уровне модуля нецелесообразен,
# т.к. меняются аргументы (83 строка, notes).


class TestContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Создаем записи в БД без сохранения
        cls.reader = User.objects.create(username='reader')
        cls.author = User.objects.create(username='author')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='title-slug',
            author=cls.author,
        )
        cls.reader_client, cls.author_client = Client(), Client()
        cls.reader_client.force_login(cls.reader)
        cls.author_client.force_login(cls.author)

    def test_note_in_user_notes_list(self):
        notes_list = (
            (self.author, self.author_client, self.note),
            (self.reader, self.reader_client, None),
        )
        url = reverse(f'{BASE_URL}list')
        for user, client, note in notes_list:
            with self.subTest(user=user.username, note=note):
                response = client.get(url)
                resp_note = response.context['object_list'].first()
                self.assertEqual(note, resp_note)

    def test_only_current_user_notes(self):
        notes = []
        cases = (
            (self.reader, self.reader_client),
            (self.author, self.author_client)
        )
        url = reverse(f'{BASE_URL}list')
        for user, client in cases:
            with self.subTest(user=user.username):
                response = client.get(url)
                resp_note = response.context['object_list'].first()
                notes.append(resp_note)
        self.assertNotEqual(notes[0], notes[1])

    def test_pages_contains_form(self):
        client = self.author_client
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,)),
        )
        for page, args in urls:
            with self.subTest(page=page):
                url = reverse(page, args=args)
                response = client.get(url)
                response_form = response.context.get('form')
                self.assertIsInstance(response_form, NoteForm)
