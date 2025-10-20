class TestCategoryModel:

    def test_category_creation(self, category):
        """
            Проверяет что объект TGUser создан с корректным tg_id.
        """
        assert category.name == "Test Category"

    def test_category_string_representation(self, category):
        """
            Проверяет строковое представление объекта Category.
        """
        strCategory = "Test Category"
        assert str(category) == strCategory


class TestTaskModel:
    def test_task_creation(self, task):
        """
            Проверяет что объект Task создан с корректным tg_id.
        """
        assert task.title == "Test Task"
        assert task.description == "Test Description"

    def test_task_string_representation(self, task):
        """
            Проверяет строковое представление объекта Category.
        """
        strTask = "Test Task"
        assert str(task) == strTask


class TestTGUserModel:
    def test_tguser_creation(self, tguser):
        """
            Проверяет что объект TGUser создан с корректным tg_id.
        """
        assert tguser.tg_id == "123456789"
