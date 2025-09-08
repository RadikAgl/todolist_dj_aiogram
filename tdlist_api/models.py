import uuid

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone


class BaseModel(models.Model):
    id = models.CharField(max_length=36, primary_key=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.id:
            timestamp_str = timezone.now().strftime("%Y%m%d%H%M%S%f")
            self.id = f"{timestamp_str}-{uuid.uuid4().hex[:8]}"  # Добавляем случайную часть
        super().save(*args, **kwargs)


class UserManager(BaseUserManager):
    def _create_user(self, tg_id, password=None, **extra_fields):
        if not tg_id:
            raise ValueError('The tg_id must be set')
        user = self.model(tg_id=tg_id)
        is_staff = extra_fields.get('is_staff', False)
        if is_staff:
            user.is_staff = True
            user.is_superuser = True
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()

        return user

    def create_superuser(self, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(**extra_fields)


class TGUser(BaseModel, AbstractBaseUser, PermissionsMixin):
    """
    Модель пользователя
    """
    tg_id = models.BigIntegerField(unique=True, db_index=True, verbose_name='Telegram ID')
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'tg_id'
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.tg_id} (ID: {self.id})"


class Category(BaseModel):
    """Модель категории задач"""
    user = models.ForeignKey(TGUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, verbose_name="категория задач")

    class Meta:
        verbose_name = "категория"
        verbose_name_plural = "категории"

    def __str__(self):
        return f'{self.name} (ID: {self.id})'


class Task(BaseModel):
    """Модель задач"""
    user = models.ForeignKey(TGUser, on_delete=models.CASCADE)
    chat_id = models.BigIntegerField(verbose_name='Идентификатор чата')
    title = models.CharField(max_length=100, verbose_name="название задачи")
    description = models.TextField(verbose_name="описание задачи", blank=True, null=True)
    categories = models.ManyToManyField(Category, related_name="task", verbose_name="категория", blank=True)
    deadline = models.DateTimeField(verbose_name="время напоминания")
    is_done = models.BooleanField(default=False, verbose_name="статус")

    class Meta:
        ordering = ["deadline"]
        verbose_name = "задача"
        verbose_name_plural = "задачи"

    def __str__(self):
        return f'{self.title} (ID: {self.id})'
