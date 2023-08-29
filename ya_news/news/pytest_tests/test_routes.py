from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects


OK = HTTPStatus.OK
FOUND = HTTPStatus.FOUND
NOT_FOUND = HTTPStatus.NOT_FOUND


pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'url, user, status',
    [
        (
            pytest.lazy_fixture('news_home_url'),
            pytest.lazy_fixture('anon_client'),
            OK
        ),
        (
            pytest.lazy_fixture('news_detail_url'),
            pytest.lazy_fixture('anon_client'),
            OK
        ),
        (
            pytest.lazy_fixture('users_login_url'),
            pytest.lazy_fixture('anon_client'),
            OK
        ),
        (
            pytest.lazy_fixture('users_logout_url'),
            pytest.lazy_fixture('anon_client'),
            OK
        ),
        (
            pytest.lazy_fixture('users_signup_url'),
            pytest.lazy_fixture('anon_client'),
            OK
        ),
        (
            pytest.lazy_fixture('news_detail_url'),
            pytest.lazy_fixture('author_client'),
            OK
        ),
        (
            pytest.lazy_fixture('news_edit_url'),
            pytest.lazy_fixture('anon_client'),
            FOUND
        ),
        (
            pytest.lazy_fixture('news_edit_url'),
            pytest.lazy_fixture('another_author_client'),
            NOT_FOUND
        ),
        (
            pytest.lazy_fixture('news_edit_url'),
            pytest.lazy_fixture('author_client'),
            OK
        ),
        (
            pytest.lazy_fixture('news_delete_url'),
            pytest.lazy_fixture('anon_client'),
            FOUND
        ),
        (
            pytest.lazy_fixture('news_delete_url'),
            pytest.lazy_fixture('another_author_client'),
            NOT_FOUND
        ),
        (
            pytest.lazy_fixture('news_delete_url'),
            pytest.lazy_fixture('author_client'),
            OK
        ),
    ]
)
def test_pages_status_code(
    url, user, status
):
    assert user.get(url).status_code == status


@pytest.mark.parametrize(
    'url, redirect_url',
    (
        (pytest.lazy_fixture('news_edit_url'),
         pytest.lazy_fixture('news_edit_redirect_url'),),
        (pytest.lazy_fixture('news_delete_url'),
         pytest.lazy_fixture('news_delete_redirect_url'),),
    ),
)
def test_redirects_for_anonymous_client(client, url, redirect_url):
    assertRedirects(client.get(url), redirect_url)
