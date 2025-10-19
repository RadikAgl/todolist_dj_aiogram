from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions
from .models import Category, Task
from .serializers import CategorySerializer, TaskListSerializer, TaskCreateUpdateSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {'user__tg_id': ['exact']}


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.none()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        'user__tg_id': ['exact'],
        'categories__id': ['exact'],
        'is_done': ['exact'],
    }

    def get_queryset(self):
        return (
            Task.objects.filter(is_done=False)
            .select_related('user')
            .prefetch_related('categories')
            .order_by('deadline')
        )

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return TaskCreateUpdateSerializer
        return TaskListSerializer
