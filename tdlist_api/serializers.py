from django.db import transaction
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
    tg_id = serializers.IntegerField(write_only=True, required=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'tg_id']

    def create(self, validated_data):
        tg_id = validated_data.pop('tg_id')
        user, _ = TGUser.objects.get_or_create(tg_id=tg_id)
        return Category.objects.create(user=user, **validated_data)


class TaskListSerializer(serializers.ModelSerializer):
    categories = serializers.SlugRelatedField(
        read_only=True, many=True, slug_field='name'
    )

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'deadline', 'created_at', 'is_done', 'categories']


class TaskCreateUpdateSerializer(serializers.ModelSerializer):
    tg_id = serializers.IntegerField(write_only=True, required=True)
    categories = serializers.PrimaryKeyRelatedField(
        many=True, required=False, queryset=Category.objects.all()
    )

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'deadline', 'chat_id', 'tg_id', 'categories', 'is_done']
        read_only_fields = ['id']

    def get_fields(self):
        fields = super().get_fields()
        tg_id = self.initial_data.get('tg_id')
        if tg_id is not None:
            fields['categories'].queryset = Category.objects.filter(user__tg_id=tg_id)
        return fields

    def validate(self, attrs):
        if not self.partial and attrs.get('deadline') is None:
            raise serializers.ValidationError({'deadline': 'Обязательное поле'})
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        tg_id = validated_data.pop('tg_id')
        categories = validated_data.pop('categories', [])
        user, _ = TGUser.objects.get_or_create(tg_id=tg_id)
        task = Task.objects.create(user=user, **validated_data)
        if categories:
            task.categories.set(categories)
        return task

    @transaction.atomic
    def update(self, instance, validated_data):
        categories = validated_data.pop('categories', None)
        instance = super().update(instance, validated_data)
        if categories is not None:
            instance.categories.set(categories)
        return instance
