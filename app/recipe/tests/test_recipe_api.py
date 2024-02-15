'''Tests for recipe API.'''
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (Recipe, Tag)

from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

RECIPES_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id):
    '''Return recipe detail URL.'''
    return reverse('recipe:recipe-detail', args=[recipe_id])


def create_recipe(user, **params):
    '''Helper function to create and return a sample recipe.'''
    defaults = {
        'title': 'Sample recipe',
        'time_minutes': 10,
        'price': Decimal('5.00'),
        'link': 'http://example.com',
        'description': 'Sample description',
    }
    defaults.update(params)
    return Recipe.objects.create(user=user, **defaults)


def create_user(**params):
    '''Helper function to create and return a sample user.'''
    return get_user_model().objects.create_user(**params)


class PublicRecipeApiTests(TestCase):
    '''Test unauthenticated API requests.'''

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        '''Test that authentication is required.'''
        res = self.client.get(RECIPES_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    '''Test authenticated API requests.'''

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email='user@example.com',
            password='password123'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        '''Test retrieving a list of recipes.'''
        create_recipe(user=self.user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipes_limited_to_user(self):
        '''Test retrieving recipes for user.'''
        user2 = create_user(
            email='user2@example.com',
            password='password123',
        )
        create_recipe(user=user2)
        create_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_recipe_detail(self):
        '''Test get recipe detail.'''
        recipe = create_recipe(user=self.user)

        url = detail_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)

    def test_create_recipe(self):
        '''Test creating recipe.'''
        payload = {
            'title': 'Chocolate cheesecake',
            'time_minutes': 30,
            'price': Decimal('5.99'),
        }
        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        for key, value in payload.items():
            self.assertEqual(getattr(recipe, key), value)
        self.assertEqual(recipe.user, self.user)

    def test_partial_update_recipe(self):
        '''Test updating a recipe with patch.'''
        recipe = create_recipe(user=self.user)

        payload = {'title': 'Chicken tikka'}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])

    def test_full_update_recipe(self):
        '''Test updating a recipe with put.'''
        recipe = create_recipe(user=self.user)

        payload = {
            'title': 'Spaghetti carbonara',
            'link': 'http://example.com/new-receipe',
            'description': 'Tasty pasta dish.',
            'time_minutes': 25,
            'price': Decimal('12.00'),
        }
        url = detail_url(recipe.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        for key, value in payload.items():
            self.assertEqual(getattr(recipe, key), value)
        self.assertEqual(recipe.user, self.user)

    def test_update_user_returns_error(self):
        '''Test updating the recipe user results in an error.'''
        new_user = create_user(
            email='user2@example.com',
            password='password123',
        )
        recipe = create_recipe(user=self.user)

        payload = {'user': new_user.id}
        url = detail_url(recipe.id)
        self.client.patch(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.user, self.user)

    def test_delete_recipe(self):
        '''Test deleting a recipe.'''
        recipe = create_recipe(user=self.user)

        url = detail_url(recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())

    def test_delete_other_user_recipe(self):
        '''Test deleting a recipe from another user returns error.'''
        new_user = create_user(
            email='user2@example.com',
            password='password123'
        )
        recipe = create_recipe(user=new_user)

        url = detail_url(recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Recipe.objects.filter(id=recipe.id).exists())

    def test_create_recipe_with_new_tag(self):
        '''Test creating a recipe with new tag.'''
        payload = {
            'title': 'Avocado lime cheesecake',
            'tags': [{"name": 'Thai'}, {"name": 'Dessert'}],
            'time_minutes': 30,
            'price': Decimal('20.00'),
        }
        res = self.client.post(RECIPES_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        self.assertEqual(recipe.tags.count(), 2)
        for tag in payload['tags']:
            exists = recipe.tags.filter(
                name=tag['name'],
                user=self.user
            ).exists()
            self.assertTrue(exists)

    def test_create_recipe_with_existing_tag(self):
        '''Test creating a recipe with existing tag.'''
        tag1 = Tag.objects.create(user=self.user, name='Thai')
        payload = {
            'title': 'Avocado lime cheesecake',
            'tags': [{"name": tag1.name}, {"name": 'Dessert'}],
            'time_minutes': 30,
            'price': Decimal('20.00'),
        }
        res = self.client.post(RECIPES_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        self.assertEqual(recipe.tags.count(), 2)
        self.assertIn(tag1, recipe.tags.all())
        for tag in payload['tags']:
            exists = recipe.tags.filter(
                name=tag['name'],
                user=self.user
            ).exists()
            self.assertTrue(exists)
