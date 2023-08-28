import pytest
from http import HTTPStatus


OK = HTTPStatus.OK
FOUND = HTTPStatus.FOUND
NOT_FOUND = HTTPStatus.NOT_FOUND


pytestmark = pytest.mark.django_db


def test_pages_status_code(
    news_home_url,
    users_login_url,
    users_logout_url,
    users_signup_url,
    news_detail_url,
    news_edit_url,
    news_delete_url,
    anon_client,
    author_client,
    another_author_client
):
    data = (
        (news_home_url, anon_client, OK),
        (news_detail_url, anon_client, OK),
        (users_login_url, anon_client, OK),
        (users_logout_url, anon_client, OK),
        (users_signup_url, anon_client, OK),
        (news_detail_url, author_client, OK),
        (news_edit_url, anon_client, FOUND),
        (news_edit_url, another_author_client, NOT_FOUND),
        (news_edit_url, author_client, OK),
        (news_delete_url, anon_client, FOUND),
        (news_delete_url, another_author_client, NOT_FOUND),
        (news_delete_url, author_client, OK),
    )
    for url, client, status in data:
        assert client.get(url).status_code == status


def test_redirects(
    news_edit_url,
    news_delete_url,
    news_edit_redirect_url,
    news_delete_redirect_url,
    anon_client
):
    data = (
        (news_edit_url, news_edit_redirect_url, anon_client),
        (news_delete_url, news_delete_redirect_url, anon_client)
    )
    for url, redirect, client in data:
        assert redirect == client.get(url).url
