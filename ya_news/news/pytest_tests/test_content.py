import pytest
from django.urls import reverse
from django.conf import settings

from news.forms import CommentForm


pytestmark = pytest.mark.django_db

anon_client = pytest.lazy_fixture('anon_client')
author_client = pytest.lazy_fixture('author_client')


@pytest.mark.usefixtures('many_news')
def test_news_count(client):
    """
    1) Количество новостей на главной странице — не более 10.
    """
    url = reverse('news:home')
    response = client.get(url)
    news = response.context['object_list']
    news_count = len(news)
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.usefixtures('many_news')
def test_news_order(client):
    """
    2) Новости отсортированы от самой свежей к самой старой.
       Свежие новости в начале списка.
    """
    url = reverse('news:home')
    response = client.get(url)
    news = list(response.context['object_list'])
    news_sorted = sorted(
        news,
        key=lambda news: news.date,
        reverse=True
    )
    assert news == news_sorted


@pytest.mark.usefixtures('many_comments')
def test_comments_order(client, news):
    """
    3) Комментарии на странице отдельной новости отсортированы
       в хронологическом порядке: старые в начале списка, новые — в конце.
    """
    url = reverse('news:detail', args=[news.id])
    response = client.get(url)
    comments = list(response.context['news'].comment_set.all())
    comments_sorted = sorted(
        comments,
        key=lambda comment: comment.created
    )
    assert comments == comments_sorted


@pytest.mark.parametrize(
    'client, control_form', (
        (author_client, CommentForm),
        (anon_client, type(None))
    )
)
def test_comment_form_availability_for_diff_users(news, client, control_form):
    """
    4) Анонимному пользователю недоступна форма для отправки комментария
       на странице отдельной новости, а авторизованному доступна.
    """
    url = reverse('news:detail', args=[news.id])
    response = client.get(url)
    response_form = response.context.get('form')
    assert isinstance(response_form, control_form)
