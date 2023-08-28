import pytest
from django.conf import settings

from news.forms import CommentForm


pytestmark = [
    pytest.mark.django_db,
    pytest.mark.usefixtures('many_news'),
    pytest.mark.usefixtures('many_comments')
]


def test_news_count(client, news_home_url):
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


@pytest.mark.parametrize(
    'client, result', (
        (pytest.lazy_fixture('author_client'), CommentForm),
        (pytest.lazy_fixture('anon_client'), type(None))
    )
)
def test_comment_form_availability_for_diff_users(
        news_detail_url,
        client,
        result
):
    response_form = client.get(news_detail_url).context.get('form')
    assert isinstance(response_form, result)
