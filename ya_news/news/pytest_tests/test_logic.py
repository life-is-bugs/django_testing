from http import HTTPStatus
from random import choice

import pytest
from django.urls import reverse
from pytest_django.asserts import assertFormError, assertRedirects

from ..forms import BAD_WORDS, WARNING
from ..models import Comment


pytestmark = pytest.mark.django_db


def test_anonymous_user_cannot_send_comment(
        client,
        news_pk,
        form_data
):
    """
    1) Анонимный пользователь не может отправить комментарий.
    """
    url = reverse('news:detail', args=news_pk)
    response = client.post(url, data=form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
    comments_count = Comment.objects.count()
    expected_comments = 0
    assert comments_count == expected_comments


def test_auth_user_can_create_comment(
        admin_user,
        admin_client,
        news,
        form_data
):
    """
    2) Авторизованный пользователь может отправить комментарий.
    """
    url = reverse('news:detail', args=[news.pk])
    response = admin_client.post(url, data=form_data)
    expected_url = url + '#comments'
    assertRedirects(response, expected_url)
    comments_count = Comment.objects.count()
    expected_comments = 1
    assert comments_count == expected_comments
    new_comment = Comment.objects.get()
    assert new_comment.text == form_data['text']
    assert new_comment.news == news
    assert new_comment.author == admin_user


def test_user_cant_use_bad_words(admin_client, news_pk):
    """
    3) Если комментарий содержит запрещённые слова, он
       не будет опубликован, а форма вернёт ошибку.
    """
    bad_words_data = {
        'text': f'Тестовый текст, содержащий {choice(BAD_WORDS)}'
    }
    url = reverse('news:detail', args=news_pk)
    response = admin_client.post(url, data=bad_words_data)
    assertFormError(response, form='form', field='text', errors=WARNING)
    comments_count = Comment.objects.count()
    expected_comments = 0
    assert comments_count == expected_comments


def test_author_can_edit_comment(
        author_client,
        news_pk,
        comment,
        form_data
):
    """
    4.1) Авторизованный пользователь может редактировать свои комментарии.
    """
    url = reverse('news:edit', args=[comment.pk])
    response = author_client.post(url, data=form_data)
    expected_url = reverse('news:detail', args=news_pk) + '#comments'
    assertRedirects(response, expected_url)
    comment.refresh_from_db()
    assert comment.text == form_data['text']


def test_author_can_delete_comment(
        author_client,
        news_pk,
        comment_pk
):
    """
    4.2) Авторизованный пользователь может удалять свои комментарии.
    """
    url = reverse('news:delete', args=comment_pk)
    response = author_client.post(url)
    expected_url = reverse('news:detail', args=news_pk) + '#comments'
    assertRedirects(response, expected_url)
    comments_count = Comment.objects.count()
    expected_comments = 0
    assert comments_count == expected_comments


def test_auth_user_cant_edit_stranger_comment(
        admin_client,
        news_pk,
        comment,
        form_data
):
    """
    5.1) Авторизованный пользователь не может редактировать
         чужие комментарии.
    """
    url = reverse('news:edit', args=[comment.pk])
    old_comment = comment.text
    response = admin_client.post(url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == old_comment


def test_other_user_cant_delete_comment(
        admin_client,
        news_pk,
        comment_pk
):
    """
    5.2) Авторизованный пользователь не может удалять
         чужие комментарии.
    """
    url = reverse('news:delete', args=comment_pk)
    response = admin_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    expected_comments = 1
    assert comments_count == expected_comments
