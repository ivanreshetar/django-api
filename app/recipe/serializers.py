'''Serializers for recipe API.'''
from rest_framework import serializers

from core.models import Recipe


class RecipeSerializer(serializers.ModelSerializer):
    '''Serializer for recipe objects.'''

    class Meta:
        model = Recipe
        fields = (
            'id', 'title', 'time_minutes', 'price', 'link', 'description',
        )
        read_only_fields = ('id',)


class RecipeDetailSerializer(RecipeSerializer):
    '''Serialize a recipe detail.'''

    class Meta:
        model = Recipe
        fields = RecipeSerializer.Meta.fields
        read_only_fields = ('id',)
