from http import HTTPStatus

import pytest
from django.urls import reverse


anon_client = pytest.lazy_fixture('anon_client')
author_client = pytest.lazy_fixture('author_client')
another_author_client = pytest.lazy_fixture('another_author_client')
news = pytest.lazy_fixture('news')
comment = pytest.lazy_fixture('comment')
LOGIN_URL = reverse('users:login')


@pytest.mark.django_db
@pytest.mark.parametrize(
    'page, obj, client, status', (
        ('news:home', None, anon_client, HTTPStatus.OK),
        ('news:detail', news, anon_client, HTTPStatus.OK),
        ('users:login', None, anon_client, HTTPStatus.OK),
        ('users:logout', None, anon_client, HTTPStatus.OK),
        ('users:signup', None, anon_client, HTTPStatus.OK),
        ('news:detail', news, author_client, HTTPStatus.OK),
        ('news:edit', comment, anon_client, HTTPStatus.FOUND),
        ('news:edit', comment, another_author_client, HTTPStatus.NOT_FOUND),
        ('news:edit', comment, author_client, HTTPStatus.OK),
        ('news:delete', comment, anon_client, HTTPStatus.FOUND),
        ('news:delete', comment, another_author_client, HTTPStatus.NOT_FOUND),
        ('news:delete', comment, author_client, HTTPStatus.OK),
    ),
)
def test_pages_status_code(
    page,
    obj,
    client,
    status
):
    if obj:
        url = reverse(page, args=[obj.id])
    else:
        url = reverse(page)
    response = client.get(url)
    assert response.status_code == status


@pytest.mark.django_db
@pytest.mark.parametrize(
    'page, obj, client', (
        ('news:edit', news, anon_client),
        ('news:delete', news, anon_client),
    ),
)
def test_redirects(page, obj, client):
    """
    4) При попытке перейти на страницу редактирования или удаления
       комментария анонимный пользователь перенаправляется на
       страницу авторизации.
    """
    url = reverse(page, args=[obj.id])
    expected_url = f'{LOGIN_URL}?next={url}'
    response = client.get(url)
    assert expected_url == response.url
