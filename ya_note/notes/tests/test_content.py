from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from ..models import Note

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

    def test_notes_list_for_different_users(self):
        """
        1) Отдельная заметка передаётся на страницу со списком
           заметок в списке object_list в словаре context;
        2) В список заметок одного пользователя не попадают заметки
           другого пользователя;
        """
        notes_list = (
            (self.author, True),
            (self.reader, False),
        )
        url = reverse('notes:list')
        for user, note in notes_list:
            self.client.force_login(user)
            with self.subTest(user=user.username, note=note):
                response = self.client.get(url)
                note_object = self.note in response.context[
                    'object_list'
                ]
                self.assertEqual(note_object, note)

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
                response = self.client.get(url)
                self.assertIn('form', response.context)
