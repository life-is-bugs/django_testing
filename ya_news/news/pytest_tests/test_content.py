import pytest
from django.conf import settings

from news.forms import CommentForm


pytestmark = pytest.mark.django_db


def test_news_count(client, many_news, news_home_url):
    news = client.get(news_home_url).context['object_list']
    news_count = len(news)
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order(client, news_home_url):
    news = list(client.get(
        news_home_url
    ).context['object_list'])
    news_sorted = sorted(
        news,
        key=lambda news: news.date,
        reverse=True
    )
    assert news == news_sorted


def test_comments_order(client, news_detail_url):
    comments = list(
        client.get(news_detail_url).context['news'].comment_set.all()
    )
    comments_sorted = sorted(
        comments,
        key=lambda comment: comment.created
    )
    assert comments == comments_sorted


def test_comment_form_availability_for_diff_users(
        news_detail_url,
        author_client,
        anon_client
):
    data = (
        (author_client, CommentForm),
        (anon_client, type(None))
    )
    for client, result in data:
        response_form = client.get(news_detail_url).context.get('form')
        assert isinstance(response_form, result)
