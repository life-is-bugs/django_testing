from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from ..forms import WARNING
from ..models import Note


User = get_user_model()


class TestNoteCreation(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.form_data = {'title': 'Заголовок',
                         'text': 'Текст',
                         'slug': 'zagolovok'}
        cls.ADD_NOTE_URL = reverse('notes:add')

    def test_user_can_create_note(self):
        self.client.force_login(self.author)
        response = self.client.post(self.ADD_NOTE_URL, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        expected_notes_count = 1
        current_notes_count = Note.objects.count()
        self.assertEqual(
            current_notes_count,
            expected_notes_count
        )
        note = Note.objects.get(slug='zagolovok')
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.slug, self.form_data['slug'])
        self.assertEqual(note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        response = self.client.post(self.ADD_NOTE_URL, data=self.form_data)
        login_url = reverse('users:login')
        expected_url = f'{login_url}?next={self.ADD_NOTE_URL}'
        self.assertRedirects(response, expected_url)
        self.assertEqual(Note.objects.count(), 0)

    def test_slug_must_be_unique(self):
        self.client.force_login(self.author)
        self.client.post(self.ADD_NOTE_URL, data=self.form_data)
        response = self.client.post(self.ADD_NOTE_URL, data=self.form_data)
        warning_message = self.form_data['slug'] + WARNING
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=warning_message
        )
        self.assertEqual(Note.objects.count(), 1)

    def test_empty_slug(self):
        self.client.force_login(self.author)
        del self.form_data['slug']
        response = self.client.post(self.ADD_NOTE_URL, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        expected_notes_count = 1
        current_notes_count = Note.objects.count()
        self.assertEqual(current_notes_count, expected_notes_count)
        note = Note.objects.get(slug='zagolovok')
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(note.slug, expected_slug)


class TestNoteEditDelete(TestCase):
    ORIGINAL_TITLE = 'Заголовок'
    ORIGINAL_TEXT = 'Текст'
    NEW_TITLE = 'Новый заголовок'
    NEW_TEXT = 'Новый текст'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='author')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='reader')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(
            title=cls.ORIGINAL_TITLE,
            text=cls.ORIGINAL_TEXT,
            slug='test-slug',
            author=cls.author,
        )
        cls.edit_note_url = reverse('notes:edit', args=[cls.note.slug])
        cls.delete_note_url = reverse('notes:delete', args=[cls.note.slug])
        cls.form_data = {
            'title': cls.NEW_TITLE,
            'text': cls.NEW_TEXT
        }

    def test_author_can_edit_note(self):
        self.author_client.post(self.edit_note_url, self.form_data)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.NEW_TITLE)
        self.assertEqual(self.note.text, self.NEW_TEXT)
        self.assertEqual(self.note.slug, 'novyij-zagolovok')
        self.assertEqual(self.note.author, self.author)

    def test_other_user_cant_edit_note(self):
        response = self.reader_client.post(self.edit_note_url, self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_from_db = Note.objects.get(id=self.note.id)
        self.assertEqual(self.note.title, note_from_db.title)
        self.assertEqual(self.note.text, note_from_db.text)
        self.assertEqual(self.note.slug, note_from_db.slug)
        self.assertEqual(self.note.author, note_from_db.author)

    def test_author_can_delete_note(self):
        response = self.author_client.post(self.delete_note_url)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 0)

    def test_other_user_cant_delete_note(self):
        response = self.reader_client.post(self.delete_note_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
