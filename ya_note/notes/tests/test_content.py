from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from ..models import Note
from ..forms import NoteForm

User = get_user_model()


class TestContent(TestCase):

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

    def test_notes_list_for_author(self):
        """
        1) Отдельная заметка передаётся на страницу со списком
           заметок в списке object_list в словаре context;
        """
        url = reverse('notes:list')
        self.client.force_login(self.author)
        with self.subTest(user=self.author.username, note=True):
            self.assertEqual(
                self.note in self.client.get(url).context[
                    'object_list'
                ],
                True
            )

    def test_notes_list_for_reader(self):
        """
        2) В список заметок одного пользователя не попадают заметки
           другого пользователя;
        """
        url = reverse('notes:list')
        self.client.force_login(self.reader)
        with self.subTest(user=self.reader.username, note=False):
            self.assertEqual(
                self.note in self.client.get(url).context[
                    'object_list'
                ],
                False
            )

    def test_pages_contains_form(self):
        """
        3) На страницы создания и редактирования заметки передаются формы.
        """
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,)),
        )
        for page, args in urls:
            with self.subTest(page=page):
                url = reverse(page, args=args)
                self.client.force_login(self.author)
                self.assertIn('form', self.client.get(url).context)
                self.assertIsInstance(
                    self.client.get(url).context['form'],
                    NoteForm
                )
