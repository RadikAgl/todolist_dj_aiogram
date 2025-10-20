from datetime import datetime

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from tdlist_api.models import Category, TGUser, Task


@pytest.fixture
def tguser(db):
    """
        Создает пользователя в модели TGUser.
    """
    return TGUser.objects.create(tg_id="123456789")


@pytest.fixture
def category(db, tguser):
    """
        Создает категорию в модели Category.
    """
    return Category.objects.create(name="Test Category", user=tguser)


@pytest.fixture
def task(db, tguser):
    """
        Создает категорию в модели Category.
    """
    return Task.objects.create(
        user=tguser,
        chat_id=123456789,
        title="Test Task",
        description="Test Description",
        deadline=datetime.now()
    )


@pytest.fixture
def api_client():
    """
        Возвращает экземпляр класса APIClient для совершения запросов к API.
    """
    return APIClient()


@pytest.fixture
def authenticated_client(api_client, django_user_model):
    username = "testuser"
    password = "testpassword"
    django_user_model.objects.create_user(username=username, password=password)

    token_url = reverse("token_obtain_pair")
    response = api_client.post(token_url, {"username": username, "password": password}, format="json")
    access_token = response.data["access"]

    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
    return api_client
