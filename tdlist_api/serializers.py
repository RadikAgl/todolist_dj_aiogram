from rest_framework import serializers

from .models import TGUser, Task, Category


class TGUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = TGUser
        fields = '__all__'

    def create(self, validated_data):
        instance, _ = TGUser.objects.get_or_create(**validated_data)
        return instance


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('name', 'id')


class TaskCreateSerializer(serializers.ModelSerializer):
    deadline = serializers.DateTimeField(format="%Y-%m-%d %H:%M")

    class Meta:
        model = Task
        fields = ('title', 'chat_id', 'description', 'deadline')


class TaskListSerializer(serializers.ModelSerializer):
    deadline = serializers.DateTimeField(format="%Y-%m-%d  %H:%M")
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M")
    categories = CategorySerializer(many=True)

    class Meta:
        model = Task
        fields = ('id', 'title', 'description', 'created_at', 'deadline', 'is_done', 'categories')
