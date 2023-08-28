from datetime import datetime, timedelta
from random import choice

import pytest
from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils import timezone
from django.test import Client
from django.urls import reverse

from news.forms import BAD_WORDS
from news.models import News, Comment


User = get_user_model()

NEWS_BASE_URL = 'news:'
USERS_BASE_URL = 'users:'


@pytest.fixture
def author():
    return User.objects.get_or_create(username='author')[0]


@pytest.fixture
def another_author():
    return User.objects.get_or_create(username='author_2')[0]


@pytest.fixture
def news():
    return News.objects.get_or_create(
        title='Заголовок', text='Текст'
    )[0]


@pytest.fixture
def author_client(author):
    author_client = Client()
    author_client.force_login(author)
    return author_client


@pytest.fixture
def another_author_client(another_author):
    another_author = User.objects.get_or_create(
        username=another_author.username)[0]
    client = Client()
    client.force_login(another_author)
    return client


@pytest.fixture
def anon_client():
    return Client()


@pytest.fixture
def comment(news, author):
    return Comment.objects.get_or_create(
        news=news,
        author=author,
        text='Текст'
    )[0]


@pytest.fixture
def form_data():
    return {
        'text': 'Новый текст комментария'
    }


@pytest.fixture
def bad_words_data():
    return {
        'text': f'Тестовый текст, содержащий {choice(BAD_WORDS)}'
    }


@pytest.fixture
def many_news():
    News.objects.bulk_create(
        News(
            title=f'Новость {index}',
            text='Текст новости',
            date=datetime.today() - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )


@pytest.fixture
def many_comments(news, author):
    now = timezone.now()
    for index in range(11):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Текст комментария {index}'
        )
        comment.created = now + timedelta(days=index)
        comment.save()


@pytest.fixture
def users_login_url():
    return reverse(f'{USERS_BASE_URL}login')


@pytest.fixture
def users_logout_url():
    return reverse(f'{USERS_BASE_URL}logout')


@pytest.fixture
def users_signup_url():
    return reverse(f'{USERS_BASE_URL}signup')


@pytest.fixture
def news_home_url():
    return reverse(f'{NEWS_BASE_URL}home')


@pytest.fixture
def news_list_url():
    return reverse(f'{NEWS_BASE_URL}list')


@pytest.fixture
def news_success_url():
    return reverse(f'{NEWS_BASE_URL}success')


@pytest.fixture
def news_home_url():
    return reverse(f'{NEWS_BASE_URL}home')


@pytest.fixture
def news_edit_url():
    return reverse(f'{NEWS_BASE_URL}edit')


@pytest.fixture
def news_detail_url(news):
    return reverse(f'{NEWS_BASE_URL}detail', args=(news.pk, ))


@pytest.fixture
def news_edit_url(comment):
    return reverse(f'{NEWS_BASE_URL}edit', args=(comment.pk, ))


@pytest.fixture
def news_delete_url(comment):
    return reverse(f'{NEWS_BASE_URL}delete', args=(comment.pk, ))


@pytest.fixture
def news_list_redirect_url(users_login_url):
    return f'{users_login_url}?next={reverse(f"{NEWS_BASE_URL}list")}'


@pytest.fixture
def news_success_redirect_url(users_login_url):
    return f'{users_login_url}?next={reverse(f"{NEWS_BASE_URL}success")}'


@pytest.fixture
def news_add_redirect_url(users_login_url):
    return f'{users_login_url}?next={reverse(f"{NEWS_BASE_URL}add")}'


@pytest.fixture
def news_detail_redirect_url(users_login_url, comment):
    next_url = reverse(f"{NEWS_BASE_URL}detail", args=(comment.pk,))
    return f"{users_login_url}?next={next_url}"


@pytest.fixture
def news_comment_hash_anchor_redirect(news):
    return reverse(f'{NEWS_BASE_URL}detail', args=(news.pk, )) + '#comments'


@pytest.fixture
def news_comment_redirect(users_login_url, news_detail_url):
    return f'{users_login_url}?next={news_detail_url}'


@pytest.fixture
def news_comment_anchor_redirect(news_detail_url):
    return news_detail_url + '#comments'


@pytest.fixture
def news_edit_redirect_url(users_login_url, news_edit_url):
    return f'{users_login_url}?next={news_edit_url}'


@pytest.fixture
def news_delete_redirect_url(users_login_url, news_delete_url):
    return f'{users_login_url}?next={news_delete_url}'
