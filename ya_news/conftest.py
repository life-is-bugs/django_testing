from datetime import datetime, timedelta

import pytest
from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils import timezone
from django.test import Client

from news.models import News, Comment

User = get_user_model()


@pytest.fixture
def author():
    author = User.objects.filter(username='author').first()
    if not author:
        author = User.objects.create(username='author')
    return author


@pytest.fixture
def news():
    news = News.objects.create(
        title='Тестовый заголовок',
        text='Тестовый текст',
    )
    return news


@pytest.fixture
def author_client():
    author = User.objects.filter(username='author').first()
    if not author:
        author = User.objects.create(username='author')
    author_client = Client()
    author_client.force_login(author)
    return author_client


@pytest.fixture
def another_author_client():
    author = User.objects.filter(username='author_2').first()
    if not author:
        author = User.objects.create(username='author_2')
    author_client = Client()
    author_client.force_login(author)
    return author_client


@pytest.fixture
def anon_client():
    anon_client = Client()
    return anon_client


@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария'
    )
    return comment


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
