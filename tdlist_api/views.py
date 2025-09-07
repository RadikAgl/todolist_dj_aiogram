from datetime import datetime

from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import TGUser, Category, Task
from .serializers import CategorySerializer, TaskCreateSerializer, TaskListSerializer

from .authentication import MyJWTAuthentication


class TelegramAuthView(APIView):
    authentication_classes = (MyJWTAuthentication,)

    def post(self, request):
        telegram_id = request.data.get('tg_id')

        if not telegram_id:
            return Response({'error': 'Нужно указать Telegram ID'}, status=status.HTTP_400_BAD_REQUEST)

        user, created = TGUser.objects.get_or_create(
            tg_id=telegram_id
        )

        refresh = RefreshToken.for_user(user)

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.filter(is_done=False)
    serializer_class = TaskListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Task.objects.filter(is_done=False)
        tg_id = self.request.query_params.get('tg_id')
        category = self.request.query_params.get('category')
        if tg_id is not None:
            queryset = queryset.filter(user__tg_id=tg_id)
        if category:
            category = Category.objects.get(id=category)
            queryset = queryset.filter(categories=category)

        return queryset

    def create(self, request, *args, **kwargs):
        data = request.data.get('data')
        tg_id = data['tg_id']
        categories = data.get('categories')
        data['deadline'] = datetime.strptime(data['date'], '%Y-%m-%d %H:%M')
        user = TGUser.objects.get(tg_id=int(tg_id))
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
        categories = data['categories']
        data['deadline'] = datetime.strptime(data['date'], '%Y-%m-%d %H:%M')
        instance = self.get_object()
        serializer = TaskCreateSerializer(instance, data=data, partial=partial)

        if serializer.is_valid():

            self.perform_update(serializer)

            if categories:
                user = TGUser.objects.get(tg_id=int(data['tg_id']))
                task = Task.objects.get(id=data['task_id'])
                add_categories_to_task(user, task, categories)

            return Response(serializer.data, status=status.HTTP_200_OK)

        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def get_category_objs(category_names, user):
    res = []
    for category in category_names.replace(' ', '').split(','):
        cats = Category.objects.filter(name__iexact=category, user=user)
        if cats:
            res.extend(cats)
        else:
            cat = Category.objects.create(name=category.lower().capitalize(), user=user)
            res.append(cat)
    return res


def add_categories_to_task(user, task, categories):
    for category in get_category_objs(categories, user):
        task.categories.add(category)
    task.save()
