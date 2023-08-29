from http import HTTPStatus
from django.urls import reverse
import pytest
from pytest_django.asserts import assertRedirects
from pytest_lazyfixture import lazy_fixture


OK = HTTPStatus.OK
FOUND = HTTPStatus.FOUND
NOT_FOUND = HTTPStatus.NOT_FOUND

LOGOUT_URL = reverse('users:logout')
SIGNUP_URL = reverse('users:signup')
HOME_URL = reverse('news:home')
DETAIL_URL = lazy_fixture('news_detail_url')
DELETE_URL = pytest.lazy_fixture('news_delete_url')
EDIT_URL = pytest.lazy_fixture('news_edit_url')
LOGIN_URL = reverse('users:login')
ADMIN_CLIENT = pytest.lazy_fixture('admin_client')
AUTHOR_CLIENT = pytest.lazy_fixture('author_client')
EDIT_REDIRECT_URL = f'{LOGIN_URL}?next={EDIT_URL}'
DELETE_REDIRECT_URL = f'{LOGIN_URL}?next={[(DELETE_URL)]}'


pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'url, client, status',
    (
        (HOME_URL, ADMIN_CLIENT, HTTPStatus.OK),
        (HOME_URL, AUTHOR_CLIENT, HTTPStatus.OK),
        (LOGIN_URL, ADMIN_CLIENT, HTTPStatus.OK),
        (LOGIN_URL, AUTHOR_CLIENT, HTTPStatus.OK),
        (LOGOUT_URL, ADMIN_CLIENT, HTTPStatus.OK),
        (LOGOUT_URL, AUTHOR_CLIENT, HTTPStatus.OK),
        (SIGNUP_URL, ADMIN_CLIENT, HTTPStatus.OK),
        (SIGNUP_URL, AUTHOR_CLIENT, HTTPStatus.OK),
        (DETAIL_URL, ADMIN_CLIENT, HTTPStatus.OK),
        (DETAIL_URL, AUTHOR_CLIENT, HTTPStatus.OK),
        (DELETE_URL, ADMIN_CLIENT, HTTPStatus.NOT_FOUND),
        (DELETE_URL, AUTHOR_CLIENT, HTTPStatus.OK),
        (EDIT_URL, ADMIN_CLIENT, HTTPStatus.NOT_FOUND),
        (EDIT_URL, AUTHOR_CLIENT, HTTPStatus.OK)
    )
)
def test_pages_status_code(
    url, client, status
):
    assert client.get(url).status_code == status


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
