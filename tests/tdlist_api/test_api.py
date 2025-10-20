from django.urls import reverse
from rest_framework import status


class TestCategoryViewset:
    def test_add_category(self, authenticated_client, tguser):
        """
        Проверяет создание категории через API.

        """
        response = authenticated_client.post(
            reverse("category-list"),
            data={"name": "New Category", "tg_id": tguser.tg_id},
            format="json",
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == "New Category"

    def test_get_categories(self, authenticated_client, tguser, category):
        """
        Проверяет получение списка категорий через API.

        """
        response = authenticated_client.get(
            reverse("category-list"),
            params={"tg_id": tguser.tg_id},
            format="json"
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data[0]["name"] == "Test Category"

    def test_get_category(self, authenticated_client, tguser, category):
        """
        Проверяет извлечение детальной информации о категории через API.

        """
        response = authenticated_client.get(
            reverse("category-detail", kwargs={"pk": category.id}),
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Test Category"

    def test_update_category(self, authenticated_client, tguser, category):
        """
        Проверяет обновление категории через API.

        """

        response = authenticated_client.patch(
            reverse("category-detail", kwargs={"pk": category.id}),
            {"name": "New Test Category", "tg_id": tguser.tg_id},
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "New Test Category"


class TestTaskViewset:
    def test_create_task(self, authenticated_client, tguser):
        """
        Проверяет создание категории через API.

        """
        response = authenticated_client.post(
            reverse("task-list"),
            data={
                "title": "New Task",
                "description": "desc",
                "chat_id": 100000,
                "tg_id": tguser.tg_id,
                "deadline": "2025-02-15 15:45"
            },
            format="json",
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["title"] == "New Task"

    def test_get_tasks(self, authenticated_client, tguser, task):
        """
        Проверяет получение списка задач через API.

        """
        response = authenticated_client.get(
            reverse("task-list"),
            params={"tg_id": tguser.tg_id},
            format="json"
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data[0]["title"] == "Test Task"

    def test_get_task(self, authenticated_client, tguser, task):
        """
        Проверяет извлечение детальной информации о категории через API.

        """
        response = authenticated_client.get(
            reverse("task-detail", kwargs={"pk": task.id}),
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == "Test Task"

    def test_update_task(self, authenticated_client, tguser, task):
        """
        Проверяет обновление категории через API.

        """

        response = authenticated_client.patch(
            reverse("task-detail", kwargs={"pk": task.id}),
            {"title": "New Test Category"},
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == "New Test Category"
