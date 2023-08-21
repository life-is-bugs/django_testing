from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects


@pytest.mark.django_db
@pytest.mark.parametrize(
    'page, args', (
        ('news:home', None),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None),
        ('news:detail', pytest.lazy_fixture('news_pk')),
    ),
)
def test_pages_availability_for_anonymous_user(client, page, args):
    """
    1) Главная страница доступна анонимному пользователю.
    2) Страница отдельной новости доступна анонимному пользователю.
    6) Страницы регистрации пользователей, входа в учётную запись
       и выхода из неё доступны анонимным пользователям.
    """
    url = reverse(page, args=args)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'page, args', (
        ('news:edit', pytest.lazy_fixture('comment_pk')),
        ('news:delete', pytest.lazy_fixture('comment_pk')),
    ),
)
def test_pages_availability_for_another_auth_user(
        author_client,
        page,
        args
):
    """
    3) Страницы удаления и редактирования комментария доступны
       автору комментария.
    """
    url = reverse(page, args=args)
    response = author_client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'page, args', (
        ('news:edit', pytest.lazy_fixture('comment_pk')),
        ('news:delete', pytest.lazy_fixture('comment_pk')),
    ),
)
def test_redirects(client, page, args):
    """
    4) При попытке перейти на страницу редактирования или удаления
       комментария анонимный пользователь перенаправляется на
       страницу авторизации.
    """
    login_url = reverse('users:login')
    url = reverse(page, args=args)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)


@pytest.mark.parametrize('page', ('news:edit', 'news:delete'))
def test_pages_availability_for_different_users(
        page,
        comment_pk,
        admin_client
):
    """
    5) Авторизованный пользователь не может зайти на страницы редактирования
       или удаления чужих комментариев (возвращается ошибка 404).
    """
    url = reverse(page, args=comment_pk)
    response = admin_client.get(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
