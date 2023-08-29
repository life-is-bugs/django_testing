from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects, assertFormError

from news.models import Comment
from news.forms import WARNING


pytestmark = [
    pytest.mark.django_db,
]


def test_anon_cant_create_comment(
    news_detail_url,
    anon_client,
    form_data,
    news_comment_redirect
):
    comments_under_post = set(Comment.objects.all())
    assert anon_client.post(
        news_detail_url, data=form_data).url == news_comment_redirect
    assert comments_under_post == set(Comment.objects.all())


def test_author_can_create_comment(
    news_detail_url,
    author,
    author_client,
    form_data,
    news_comment_hash_anchor_redirect
):
    comments_under_post = set(Comment.objects.all())
    response = author_client.post(news_detail_url, data=form_data)
    assert response.url == news_comment_hash_anchor_redirect
    new_comments = (
        set(Comment.objects.all()) - comments_under_post
    )
    assert len(new_comments) == 1
    new_comment = new_comments.pop()
    assert new_comment.author == author
    assert new_comment.text == form_data['text']
    assert new_comment.author == author


def test_user_cant_use_bad_words(
        author_client,
        news_detail_url,
        bad_words_data
):
    comments_under_post = set(Comment.objects.all())
    response = author_client.post(news_detail_url, data=bad_words_data)
    assertFormError(response, form='form', field='text', errors=WARNING)
    assert comments_under_post == set(Comment.objects.all())


def test_author_can_edit_comment(
        author_client,
        author,
        news_edit_url,
        comment,
        form_data
):
    author_client.post(news_edit_url, data=form_data)
    updated_comment = Comment.objects.get(id=comment.id)
    assert comment == updated_comment
    assert comment.text == form_data['text']
    assert comment.news == updated_comment.news
    assert comment.author == updated_comment.author


def test_author_can_delete_comment(
        author_client,
        news_delete_url,
        news_comment_anchor_redirect,
        comment
):
    response = author_client.post(news_delete_url)
    assertRedirects(response, news_comment_anchor_redirect)
    assert not Comment.objects.filter(pk=comment.pk).exists()


def test_auth_user_cant_edit_stranger_comment(
        admin_client,
        news_edit_url,
        comment,
        form_data
):
    response = admin_client.post(news_edit_url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND

    comment_after_post = Comment.objects.get(id=comment.id)
    assert comment_after_post == comment
    assert comment_after_post.text == comment.text
    assert comment_after_post.news == comment.news
    assert comment_after_post.author == comment.author


def test_other_user_cant_delete_comment(
        admin_client,
        news_delete_url,
        comment
):
    assert admin_client.post(
        news_delete_url).status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.filter(pk=comment.pk).exists()
