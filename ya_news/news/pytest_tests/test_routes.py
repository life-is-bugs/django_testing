from http import HTTPStatus

import pytest


@pytest.mark.django_db
@pytest.mark.parametrize(
    'url, client, status', (
        (pytest.lazy_fixture('news_home_url'),
         pytest.lazy_fixture('anon_client'), HTTPStatus.OK),
        (pytest.lazy_fixture('news_detail_url'),
         pytest.lazy_fixture('anon_client'), HTTPStatus.OK),
        (pytest.lazy_fixture('users_login_url'),
         pytest.lazy_fixture('anon_client'), HTTPStatus.OK),
        (pytest.lazy_fixture('users_logout_url'),
         pytest.lazy_fixture('anon_client'), HTTPStatus.OK),
        (pytest.lazy_fixture('users_signup_url'),
         pytest.lazy_fixture('anon_client'), HTTPStatus.OK),
        (pytest.lazy_fixture('news_detail_url'),
         pytest.lazy_fixture('author_client'), HTTPStatus.OK),
        (pytest.lazy_fixture('news_edit_url'),
         pytest.lazy_fixture('anon_client'), HTTPStatus.FOUND),
        (pytest.lazy_fixture('news_edit_url'),
         pytest.lazy_fixture('another_author_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('news_edit_url'),
         pytest.lazy_fixture('author_client'), HTTPStatus.OK),
        (pytest.lazy_fixture('news_delete_url'),
         pytest.lazy_fixture('anon_client'), HTTPStatus.FOUND),
        (pytest.lazy_fixture('news_delete_url'),
         pytest.lazy_fixture('another_author_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('news_delete_url'),
         pytest.lazy_fixture('author_client'), HTTPStatus.OK),
    ),
)
def test_pages_status_code(
    url,
    client,
    status
):
    assert client.get(url).status_code == status


@pytest.mark.django_db
@pytest.mark.parametrize(
    'url, redirect, client', (
        (pytest.lazy_fixture('news_edit_url'),
         pytest.lazy_fixture('news_edit_redirect_url'),
         pytest.lazy_fixture('anon_client')),
        (pytest.lazy_fixture('news_delete_url'),
         pytest.lazy_fixture('news_delete_redirect_url'),
         pytest.lazy_fixture('anon_client')),
    ),
)
def test_redirects(url, redirect, client):
    assert redirect == client.get(url).url
