import os

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from dotenv import load_dotenv

load_dotenv(os.path.join("...", ".env"))


class Command(BaseCommand):
    help = 'Создает сервисного пользователя'

    def handle(self, *args, **options):
        PASSWORD = os.getenv('BOT_PASSWORD')
        USERNAME = os.getenv('BOT_USERNAME')
        User = get_user_model()

        user, created = User.objects.get_or_create(
            username=USERNAME
        )
        if created:
            user.set_password(PASSWORD)
            user.save()
