from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from ..forms import WARNING
from ..models import Note


User = get_user_model()
NOTES_BASE_URL = 'notes:'
USERS_BASE_URL = 'users:'

# Расчёт урлов на уровне модуля нецелесообразен,
# т.к. меняются аргументы (80 строка, notes).


class TestNoteCreation(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.anon = User.objects.create(username='anon')
        cls.author = User.objects.create(username='Автор')
        cls.form_data = {'title': 'Заголовок',
                         'text': 'Текст',
                         'slug': 'zagolovok'}

        cls.anon_client = Client()
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

    def test_user_can_create_note(self):
        # Т.к. понятие авторизации существует в данном проекте только
        # посредством запросов, нет возможности проверить факт создания
        # записи иначе, чем через запрос post непосредственно от пользователя.
        ADD_NOTE_URL = reverse('notes:add')
        REDIRECT_NOTE_URL = reverse('notes:success')

        response = self.author_client.post(ADD_NOTE_URL, data=self.form_data)
        self.assertRedirects(response, REDIRECT_NOTE_URL)

        note = Note.objects.filter(author=self.author).first()
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.slug, self.form_data['slug'])
        self.assertEqual(note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        ADD_NOTE_URL = reverse('notes:add')
        REDIRECT_NOTE_URL = reverse('users:login') + r"?next=%2Fadd%2F"

        response = self.anon_client.post(ADD_NOTE_URL, data=self.form_data)
        self.assertRedirects(response, REDIRECT_NOTE_URL)

        anons_note = Note.objects.filter(
            author=self.anon).first()
        self.assertEqual(anons_note, None)

    def test_slug_must_be_unique(self):
        ADD_NOTE_URL = reverse('notes:add')
        for _ in range(2):
            response = self.author_client.post(
                ADD_NOTE_URL, data=self.form_data
            )
        author_notes_count = Note.objects.filter(author=self.author).count()
        author_notes_count_must_be = 1
        self.assertEqual(author_notes_count, author_notes_count_must_be)
        warning_message = self.form_data['slug'] + WARNING
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=warning_message
        )

    def test_empty_slug(self):
        ADD_NOTE_URL = reverse('notes:add')
        del self.form_data['slug']
        self.author_client.post(
            ADD_NOTE_URL, data=self.form_data
        )
        new_note = Note.objects.filter(author=self.author).first()
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(new_note.author, self.author)
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, expected_slug)


class TestNoteEditDelete(TestCase):
    ORIGINAL_TITLE = 'Заголовок'
    ORIGINAL_TEXT = 'Текст'
    NEW_TITLE = 'Новый заголовок'
    NEW_TEXT = 'Новый текст'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='author')
        cls.reader = User.objects.create(username='reader')
        cls.note = Note.objects.create(
            title=cls.ORIGINAL_TITLE,
            text=cls.ORIGINAL_TEXT,
            slug='note-slug',
            author=cls.author,
        )

        cls.author_client, cls.reader_client = Client(), Client()
        cls.author_client.force_login(cls.author)
        cls.reader_client.force_login(cls.reader)

        cls.edit_note_url = reverse('notes:edit', args=[cls.note.slug])
        cls.delete_note_url = reverse('notes:delete', args=[cls.note.slug])
        cls.form_data = {
            'title': cls.NEW_TITLE,
            'text': cls.NEW_TEXT}

    def test_author_can_edit_note(self):
        self.author_client.post(self.edit_note_url, self.form_data)
        self.note.refresh_from_db()
        expected_slug = slugify(self.form_data['title'])

        self.assertEqual(self.note.author, self.author)
        self.assertEqual(self.note.title, self.NEW_TITLE)
        self.assertEqual(self.note.text, self.NEW_TEXT)
        self.assertEqual(self.note.slug, expected_slug)

    def test_other_user_cant_edit_note(self):
        response = self.reader_client.post(self.edit_note_url, self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_from_db = Note.objects.get(id=self.note.id)

        self.assertEqual(self.note.author, note_from_db.author)
        self.assertEqual(self.note.slug, note_from_db.slug)
        self.assertEqual(self.note.title, note_from_db.title)
        self.assertEqual(self.note.text, note_from_db.text)

    def test_author_can_delete_note(self):
        response = self.author_client.post(self.delete_note_url)
        self.assertRedirects(response, reverse('notes:success'))
        note = Note.objects.filter(author=self.author).first()
        self.assertEqual(note, None)

    def test_other_user_cant_delete_note(self):
        response = self.reader_client.post(self.delete_note_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_from_db = Note.objects.filter(author=self.author).first()
        self.assertEqual(self.note.author, note_from_db.author)
        self.assertEqual(self.note.slug, note_from_db.slug)
        self.assertEqual(self.note.title, note_from_db.title)
        self.assertEqual(self.note.text, note_from_db.text)
