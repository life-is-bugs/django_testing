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


class TestNoteCreation(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.anon = User.objects.create(username='anon')
        cls.author = User.objects.create(username='Автор')
        cls.form_data = {'title': 'Заголовок',
                         'text': 'Текст',
                         'slug': 'slug'}
        cls.anon_client = Client()
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

    def test_user_can_create_note(self):
        author_notes_count_must_be = Note.objects.all().count() + 1
        response = self.author_client.post(NOTES_ADD_URL, data=self.form_data)
        self.assertRedirects(response, NOTES_SUCCESS_URL)
        notes_count = Note.objects.all().count()
        self.assertEqual(notes_count, author_notes_count_must_be)
        note = Note.objects.filter(slug=self.form_data['slug']).first()
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.slug, self.form_data['slug'])
        self.assertEqual(note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        author_notes_count_must_be = Note.objects.all().count()
        response = self.anon_client.post(NOTES_ADD_URL, data=self.form_data)
        self.assertRedirects(response, NOTES_ADD_REDIRECT_URL)
        notes_count = Note.objects.all().count()
        self.assertEqual(notes_count, author_notes_count_must_be)
        anons_note = Note.objects.filter(slug=self.form_data['slug']).exists()
        self.assertEqual(anons_note, False)

    def test_slug_must_be_unique(self):
        for _ in range(2):
            response = self.author_client.post(
                NOTES_ADD_URL, data=self.form_data
            )
        author_notes_count = Note.objects.filter(
            slug=self.form_data['slug']
        ).count()
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
        form_current_slug = self.form_data.pop('slug')
        self.author_client.post(
            NOTES_ADD_URL, data=self.form_data
        )
        new_with_old_slug = Note.objects.filter(
            slug=form_current_slug).exists()
        self.assertEqual(new_with_old_slug, False)
        expected_slug = slugify(self.form_data['title'])
        new_note = Note.objects.filter(slug=expected_slug).first()
        self.assertEqual(new_note.author, self.author)
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, expected_slug)


class TestNoteEditDelete(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='author')
        cls.reader = User.objects.create(username='reader')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='slug',
            author=cls.author,
        )
        cls.author_client, cls.reader_client = Client(), Client()
        cls.author_client.force_login(cls.author)
        cls.reader_client.force_login(cls.reader)
        cls.form_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'new-slug'
        }

    def test_author_can_edit_note(self):
        self.author_client.post(NOTES_EDIT_URL, self.form_data)
        self.note.refresh_from_db()
        self.assertEqual(self.note.author, self.author)
        self.assertEqual(self.note.title, self.form_data['title'])
        self.assertEqual(self.note.text, self.form_data['text'])
        self.assertEqual(self.note.slug, self.form_data['slug'])

    def test_other_user_cant_edit_note(self):
        response = self.reader_client.post(NOTES_EDIT_URL, self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_from_db = Note.objects.filter(pk=self.note.id).first()
        self.assertEqual(self.note.author, note_from_db.author)
        self.assertEqual(self.note.slug, note_from_db.slug)
        self.assertEqual(self.note.title, note_from_db.title)
        self.assertEqual(self.note.text, note_from_db.text)

    def test_author_can_delete_note(self):
        response = self.author_client.post(NOTES_DELETE_URL)
        self.assertRedirects(response, NOTES_SUCCESS_URL)
        note = Note.objects.filter(author=self.author).exists()
        self.assertEqual(note, False)

    def test_other_user_cant_delete_note(self):
        response = self.reader_client.post(NOTES_DELETE_URL)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_from_db = Note.objects.filter(slug=self.note.slug).first()
        self.assertEqual(self.note.author, note_from_db.author)
        self.assertEqual(self.note.slug, note_from_db.slug)
        self.assertEqual(self.note.title, note_from_db.title)
        self.assertEqual(self.note.text, note_from_db.text)
