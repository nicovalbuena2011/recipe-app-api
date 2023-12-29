"""
Test for the ingredients API.
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    Ingredients,
    Recipe
)

from recipe.serializers import IngredientSerializer

INGREDIENTS_URL = reverse('recipe:ingredients-list')

def detail_url(ingredient_id):
    """create and return a tag detail URL."""
    return reverse('recipe:ingredients-detail', args = [ingredient_id])

def create_user(email = 'user@example.com', password = 'testpass123'):
    """Create and return user."""
    return get_user_model().objects.create_user(email = email, password = password)

def create_ingredients(user , **params):
    """Create and return a ingredient"""
    defaults = {
        'name': 'sample ingredient',
    }
    defaults.update(params)

    recipe = Ingredients.objects.create(user = user, **defaults)
    return recipe

def detail_url(ingredient_id):
    """create and return a ingredient detail URL."""
    return reverse('recipe:ingredients-detail', args = [ingredient_id])

class PublicIngredientsApiTest(TestCase):
    """Test unauthenticated API request"""

    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required for retrievering ingredients"""
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateIngredientsApiTest(TestCase):
    """Test authenticated API request"""

    def setUp(self) -> None:
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredients(self):
        """Test for retrieving a list of ingredients."""
        # create_ingredients(self.user)
        # create_ingredients(self.user)
        Ingredients.objects.create(name = 'sample ingredient', user = self.user)
        Ingredients.objects.create(name = 'sample ingredient2', user = self.user)

        res = self.client.get(INGREDIENTS_URL)
        ingredients = Ingredients.objects.all().order_by('-name')

        serializer = IngredientSerializer(ingredients, many = True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """Test list of ingredients is limited to authenticated user."""
        # create_ingredients(self.user)
        ingredient = Ingredients.objects.create(name = 'sample ingredient', user = self.user)

        user2 = create_user(
            email = 'email2@example.com',
            password = 'testpass123'
        )
        # create_ingredients(user2)
        Ingredients.objects.create(name = 'sample ingredient2', user = user2)

        res = self.client.get(INGREDIENTS_URL)
        # print(f'{res.data}------{ingredient}')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data[0]['name'], ingredient.name)
        self.assertEqual(res.data[0]['id'], ingredient.id)
        self.assertEqual(len(res.data), 1)

    def test_update_ingredient(self):
        """Test updating an ingredient."""
        payload = {
            'name': 'updated ingredient'
        }
        ingredient = Ingredients.objects.create(name = 'sample ingredient', user = self.user)

        url = detail_url(ingredient.id)
        res = self.client.patch(url, payload)
        ingredient.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(ingredient.name, payload['name'])

    def test_delete_ingredients(self):
        """Test deleting an ingredient."""
        ingredient = Ingredients.objects.create(name = 'sample ingredient', user = self.user)

        url = detail_url(ingredient.id)
        res = self.client.delete(url)
        
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        ingredients = Ingredients.objects.filter(user = self.user)
        self.assertFalse(ingredients.exists())

    def test_filter_ingredients_assigned_to_recipes(self):
        """Test listing ingredients to those assigned recipes."""
        in1 = Ingredients.objects.create(user = self.user, name = 'Apples')
        in2 = Ingredients.objects.create(user = self.user, name = 'Turkey')
        recipe = Recipe.objects.create(
            title = 'Apple Crumble',
            time_minutes = 5,
            price = Decimal('4.50'),
            user = self.user
        )
        recipe.ingredients.add(in1)

        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})

        s1 = IngredientSerializer(in1)
        s2 = IngredientSerializer(in2)
        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)

    def test_filtered_ingredients_unique(self):
        """Test filtered ingredients return a unique list."""
        ing = Ingredients.objects.create(user = self.user, name = 'Eggs')
        Ingredients.objects.create(user = self.user, name = 'Lentils')
        recipe1 = Recipe.objects.create(
            title = 'Eggs benedict',
            time_minutes = 5,
            price = Decimal('4.50'),
            user = self.user
        )
        recipe2 = Recipe.objects.create(
            title = 'Herb Eggs',
            time_minutes = 7,
            price = Decimal('4.50'),
            user = self.user
        )
        recipe1.ingredients.add(ing)
        recipe2.ingredients.add(ing)

        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)