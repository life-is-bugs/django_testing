from http import HTTPStatus
from random import choice

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects, assertFormError

from news.models import Comment
from news.forms import BAD_WORDS, WARNING

author = pytest.lazy_fixture('author')

anon_client = pytest.lazy_fixture('anon_client')
author_client = pytest.lazy_fixture('author_client')

news = pytest.lazy_fixture('news')
comment = pytest.lazy_fixture('comment')
LOGIN_URL = reverse('users:login')


@pytest.mark.django_db
@pytest.mark.parametrize(
    'page, obj, client, form_data, redirect, result', (
        (
            'news:detail',
            news,
            anon_client,
            {'text': 'Комментарий от Анонима'},
            '/auth/login/?next=/news/1/',
            type(None)
        ),
        (
            'news:detail',
            news,
            author_client,
            {'text': 'Комментарий от Автора'},
            '/news/1/#comments',
            Comment
        ),
    ),
)
def test_create_comment(
    page,
    obj,
    client,
    form_data,
    redirect,
    result
):
    url = reverse(page, args=[obj.id])
    response = client.post(url, data=form_data)
    assert response.url == redirect
    comment = Comment.objects.filter(**form_data).first()
    assert isinstance(comment, result)


def test_user_cant_use_bad_words(admin_client, news):
    """
    3) Если комментарий содержит запрещённые слова, он
       не будет опубликован, а форма вернёт ошибку.
    """
    bad_words_data = {
        'text': f'Тестовый текст, содержащий {choice(BAD_WORDS)}'
    }
    url = reverse('news:detail', args=[news.id, ])
    response = admin_client.post(url, data=bad_words_data)
    assertFormError(response, form='form', field='text', errors=WARNING)
    comment = Comment.objects.filter(**bad_words_data).first()
    assert isinstance(comment, type(None))


@pytest.mark.django_db
def test_author_can_edit_comment(
        author_client,
        news,
        comment,
        form_data
):
    """
    4.1) Авторизованный пользователь может редактировать свои комментарии.
    """
    url = reverse('news:edit', args=[comment.id, ])
    response = author_client.post(url, data=form_data)
    expected_url = reverse('news:detail', args=[news.id, ]) + '#comments'
    assertRedirects(response, expected_url)
    comment.refresh_from_db()
    assert comment.text == form_data['text']
    assert comment.author.username == author.name


@pytest.mark.django_db
def test_author_can_delete_comment(
        author_client,
        news,
        comment
):
    """
    4.2) Авторизованный пользователь может удалять свои комментарии.
    """
    url = reverse('news:delete', args=[news.id, ])
    response = author_client.post(url)
    expected_url = reverse('news:detail', args=[comment.id, ]) + '#comments'
    assertRedirects(response, expected_url)
    comment = Comment.objects.filter(id=comment.id).first()
    expected_comment = None
    assert comment == expected_comment


@pytest.mark.django_db
def test_auth_user_cant_edit_stranger_comment(
        admin_client,
        news,
        comment,
        form_data
):
    """
    5.1) Авторизованный пользователь не может редактировать
         чужие комментарии.
    """
    url = reverse('news:edit', args=[comment.id, ])
    old_comment = comment
    response = admin_client.post(url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment == old_comment


def test_other_user_cant_delete_comment(
        admin_client,
        news,
        comment
):
    """
    5.2) Авторизованный пользователь не может удалять
         чужие комментарии.
    """
    url = reverse('news:delete', args=[comment.id, ])
    response = admin_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment = Comment.objects.filter(id=comment.id).first()
    assert isinstance(comment, Comment)
