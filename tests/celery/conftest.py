import pytest


from tdlist_api.models import TGUser


@pytest.fixture
def tguser(db):
    """
        Создает пользователя в модели TGUser.
    """
    return TGUser.objects.create(tg_id="123456789")
