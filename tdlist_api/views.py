from datetime import datetime

from django.utils import timezone
from rest_framework import viewsets, status, permissions
from rest_framework.response import Response


from .models import TGUser, Category, Task
from .serializers import CategorySerializer, TaskCreateSerializer, TaskListSerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Category.objects.all()
        tg_id = self.request.query_params.get('tg_id')
        if tg_id:
            user, _ = TGUser.objects.get_or_create(tg_id=int(tg_id))
            queryset = queryset.filter(user=user)
        return queryset

    def create(self, request, *args, **kwargs):
        data = request.data.get('data')
        tg_id = data['tg_id']
        user, created = TGUser.objects.get_or_create(tg_id=int(tg_id))
        serializer = CategorySerializer(data=data)
        if serializer.is_valid():
            serializer.save(user=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.filter(is_done=False)
    serializer_class = TaskListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Task.objects.all().filter(is_done=False)
        tg_id = self.request.query_params.get('tg_id')
        if tg_id:
            user, _ = TGUser.objects.get_or_create(tg_id=int(tg_id))
            queryset = queryset.filter(user=user)
        category = self.request.query_params.get('category')
        if category:
            category = Category.objects.get(id=category)
            queryset = queryset.filter(categories=category)

        return queryset

    def create(self, request, *args, **kwargs):
        data = request.data.get('data')
        tg_id = data['tg_id']
        categories = data.get('categories')
        deadline = datetime.strptime(data['date'], '%Y-%m-%d %H:%M')
        data['deadline'] = timezone.make_aware(deadline, timezone.get_current_timezone())
        user, created = TGUser.objects.get_or_create(tg_id=int(tg_id))
        serializer = TaskCreateSerializer(data=data)

        if serializer.is_valid():

            task = serializer.save(user=user)

            if categories:
                for category in get_category_objs(categories, user):
                    task.categories.add(category)
            task.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, *args, **kwargs):
        partial = True
        data = request.data
        categories = data.get('categories')
        date = data.get('date')
        if date:
            data['deadline'] = datetime.strptime(date, '%Y-%m-%d %H:%M')
        instance = self.get_object()
        serializer = TaskCreateSerializer(instance, data=data, partial=partial)

        if serializer.is_valid():

            self.perform_update(serializer)

            if categories:
                user = TGUser.objects.get(tg_id=int(data['tg_id']))
                task = Task.objects.get(id=data['task_id'])
                task.categories.clear()
                add_categories_to_task(user, task, categories)

            return Response(serializer.data, status=status.HTTP_200_OK)

        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def get_category_objs(categories, user):
    res = []
    for category in categories:
        cats = Category.objects.filter(id=category, user=user)
        if cats:
            res.extend(cats)
    return res


def add_categories_to_task(user, task, categories):
    for category in get_category_objs(categories, user):
        task.categories.add(category)
    task.save()
