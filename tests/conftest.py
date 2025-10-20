import os

import django
from dotenv import load_dotenv


def pytest_sessionstart(session):
    load_dotenv(os.path.join(".", ".env"))
    django.setup()
