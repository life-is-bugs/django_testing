from http import HTTPStatus
from random import choice

import pytest
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_create_comment_by_anon(
    news_detail_url,
    anon_client,
    form_data,
    news_hash_anchor_news_redirect
):
    assert anon_client.post(
        news_detail_url, data=form_data).url == news_hash_anchor_news_redirect
    comment = Comment.objects.filter(**form_data).exists()
    assert comment is False


@pytest.mark.django_db
def test_create_comment_by_author(
    news_detail_url,
    author,
    author_client,
    form_data,
    news,
    news_hash_anchor_comment_redirect
):
    comments_count_extends = Comment.objects.all().count() + 1
    response = author_client.post(news_detail_url, data=form_data)
    assert response.url == news_hash_anchor_comment_redirect

    comment = Comment.objects.filter(
        author=author,
        text=form_data['text'],
        news=news,
    ).exists()
    assert comment is True

    comments_count = Comment.objects.all().count()
    assert comments_count_extends == comments_count


def test_user_cant_use_bad_words(admin_client, news_detail_url):
    bad_words_data = {
        'text': f'Тестовый текст, содержащий {choice(BAD_WORDS)}'
    }
    response = admin_client.post(news_detail_url, data=bad_words_data)
    assertFormError(response, form='form', field='text', errors=WARNING)
    comment = Comment.objects.filter(**bad_words_data).exists()
    assert comment is False


@pytest.mark.django_db
def test_author_can_edit_comment(
        author_client,
        news_edit_url,
        news_hash_anchor_comment_redirect,
        comment,
        form_data
):
    old_comment = comment
    response = author_client.post(news_edit_url, data=form_data)
    assertRedirects(response, news_hash_anchor_comment_redirect)
    comment.refresh_from_db()
    assert comment == old_comment
    assert comment.text == old_comment.text
    assert comment.news == old_comment.news
    assert comment.author == old_comment.author


@pytest.mark.django_db
def test_author_can_delete_comment(
        author_client,
        news_delete_url,
        news_hash_anchor_comment_redirect,
        comment
):
    assertRedirects(author_client.post(news_delete_url),
                    news_hash_anchor_comment_redirect
                    )
    comment = Comment.objects.filter(id=comment.id).exists()
    assert comment is False


@pytest.mark.django_db
def test_auth_user_cant_edit_stranger_comment(
        admin_client,
        news_edit_url,
        comment,
        form_data
):
    old_comment = comment
    response = admin_client.post(news_edit_url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment == old_comment
    assert comment.text == old_comment.text
    assert comment.news == old_comment.news
    assert comment.author == old_comment.author


def test_other_user_cant_delete_comment(
        admin_client,
        news_delete_url,
        comment
):
    assert admin_client.post(
        news_delete_url).status_code == HTTPStatus.NOT_FOUND
    comment = Comment.objects.filter(id=comment.id).exists()
    assert comment is True
