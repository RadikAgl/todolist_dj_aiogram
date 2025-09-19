from django.contrib import admin

from .models import Task, Category, TGUser


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """Настройки отображения задач в интерфейсе администратора"""
    filter_horizontal = ('categories',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Настройки отображения категорий в интерфейсе администратора"""
    pass


@admin.register(TGUser)
class TGUserAdmin(admin.ModelAdmin):
    """Настройки отображения категорий в интерфейсе администратора"""
    pass
