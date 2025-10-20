from datetime import timedelta

import pytest
from django.utils import timezone

from tdlist_api.models import Task
from tdlist_api.tasks import get_hot_tasks


@pytest.mark.django_db
def test_get_hot_tasks_sends_reminders_for_tasks_in_window(mocker, tguser):
    now = timezone.now()

    t_in_1 = Task.objects.create(
        user=tguser,
        chat_id=123456789,
        title="Test",
        description="Desc",
        is_done=False,
        deadline=now + timedelta(seconds=10)
    )
    t_in_2 = Task.objects.create(
        user=tguser,
        chat_id=123456789,
        title="Test",
        description="Desc",
        is_done=False,
        deadline=now - timedelta(seconds=10)
    )

    t_out_future = Task.objects.create(
        user=tguser,
        chat_id=123456789,
        title="Test",
        description="Desc",
        is_done=False,
        deadline=now + timedelta(seconds=30)
    )
    t_out_past = Task.objects.create(
        user=tguser,
        chat_id=123456789,
        title="Test",
        description="Desc",
        is_done=False,
        deadline=now - timedelta(seconds=30)
    )

    t_done = Task.objects.create(
        user=tguser,
        chat_id=123456789,
        title="Test",
        description="Desc",
        is_done=True,
        deadline=now
    )

    send_mock = mocker.patch('tdlist_api.tasks.send_reminder')

    get_hot_tasks.run()

    assert send_mock.call_count == 2
    send_mock.assert_has_calls([mocker.call(t_in_1), mocker.call(t_in_2)], any_order=True)
