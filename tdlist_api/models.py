import uuid

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, Permission
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone


class BaseModel(models.Model):
    id = models.CharField(max_length=36, primary_key=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.id:
            timestamp_str = timezone.now().strftime("%Y%m%d%H%M%S%f")
            self.id = f"{timestamp_str}-{uuid.uuid4().hex[:8]}"  # Добавляем случайную часть
        super().save(*args, **kwargs)


class TGUser(BaseModel):
    """
    Модель пользователя телеграм
    """
    tg_id = models.BigIntegerField(unique=True, db_index=True, verbose_name='Telegram ID')

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
