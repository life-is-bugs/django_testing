from datetime import datetime, timedelta

import pytest
from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils import timezone
from django.test import Client
from django.urls import reverse

from news.models import News, Comment

User = get_user_model()

NEWS_BASE_URL = 'news:'
USERS_BASE_URL = 'users:'
USERS_LOGIN_URL = reverse(f'{USERS_BASE_URL}login')


@pytest.fixture
def author():
    return User.objects.get_or_create(username='author')[0]


@pytest.fixture
def news():
    return News.objects.get_or_create(
        title='Заголовок', text='Текст',
    )[0]


@pytest.fixture
def author_client(author):
    author_client = Client()
    author_client.force_login(author)
    return author_client


@pytest.fixture
def another_author_client():
    author = User.objects.get_or_create(username='author_2')[0]
    client = Client()
    client.force_login(author)
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
def news_add_url():
    return reverse(f'{NEWS_BASE_URL}add')


@pytest.fixture
def news_detail_url():
    news = News.objects.get_or_create(
        title='Заголовок', text='Текст',
    )[0]
    return reverse(f'{NEWS_BASE_URL}detail', kwargs={'pk': news.pk})


@pytest.fixture
def news_edit_url():
    author = User.objects.get_or_create(username='author')[0]
    news = News.objects.get_or_create(
        title='Заголовок', text='Текст',
    )[0]
    comment = Comment.objects.get_or_create(
        news=news,
        author=author,
        text='Текст'
    )[0]
    return reverse(
        f'{NEWS_BASE_URL}edit',
        kwargs={'pk': comment.pk}
    )


@pytest.fixture
def news_delete_url(comment):
    return reverse(
        f'{NEWS_BASE_URL}delete',
        kwargs={'pk': comment.pk}
    )


@pytest.fixture
def news_list_redirect_url():
    return f'{USERS_LOGIN_URL}?next={reverse(f"{NEWS_BASE_URL}list")}'


@pytest.fixture
def news_success_redirect_url():
    return f'{USERS_LOGIN_URL}?next={reverse(f"{NEWS_BASE_URL}success")}'


@pytest.fixture
def news_add_redirect_url():
    return f'{USERS_LOGIN_URL}?next={reverse(f"{NEWS_BASE_URL}add")}'


@pytest.fixture
def news_detail_redirect_url(comment):
    next_url = reverse(f"{NEWS_BASE_URL}detail", kwargs={"pk": comment.pk})
    return f'{USERS_LOGIN_URL}?next={next_url}'


@pytest.fixture
def news_hash_anchor_comment_redirect(news):
    return f'/news/{news.pk}/#comments'


@pytest.fixture
def news_hash_anchor_news_redirect(news):
    return f'{USERS_LOGIN_URL}?next=/news/{news.pk}/'


@pytest.fixture
def news_edit_redirect_url(comment):
    next_url = reverse(f"{NEWS_BASE_URL}edit", kwargs={"pk": comment.pk})
    return f'{USERS_LOGIN_URL}?next={next_url}'


@pytest.fixture
def news_delete_redirect_url(comment):
    next_url = reverse(f"{NEWS_BASE_URL}delete", kwargs={"pk": comment.pk})
    return f'{USERS_LOGIN_URL}?next={next_url}'
