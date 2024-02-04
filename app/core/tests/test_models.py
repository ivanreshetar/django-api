'''Tests for models'''
from django.test import TestCase
from django.contrib.auth import get_user_model

from decimal import Decimal

from core import models


def create_user(email='user@example.com', password='test123'):
    '''Create a user'''
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):
    '''Test models'''
    def test_create_user_with_email_successful(self):
        '''Test creating a new user with an email is successful'''
        email = 'test@example.com'
        password = 'Testpass123'
        user = create_user(
            email=email,
            password=password,
        )
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        '''Test the email for a new user is normalized'''
        sample_emails = [
            ['test1@EXAMPLE.COM', 'test1@example.com'],
            ['Test2@Example.COM', 'Test2@example.com'],
            ['TEST3@EXAMPLE.COM', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com'],
        ]
        for email, expected in sample_emails:
            user = create_user(email, 'test123')
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        '''Test creating user without email raises error'''
        with self.assertRaises(ValueError):
            create_user('', 'test123')

    def test_create_new_superuser(self):
        '''Test creating a new superuser'''
        user = get_user_model().objects.create_superuser(
            'test@example.com',
            'test123',
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_recipe(self):
        '''Test creating a recipe'''
        user = create_user(
            'test@example.com',
            'testpass123',
        )
        recipe = models.Recipe.objects.create(
            user=user,
            title='Test recipe',
            time_minutes=5,
            price=Decimal('10.00'),
            description='Test recipe description',
        )

        self.assertEqual(str(recipe), recipe.title)

    def test_create_tag(self):
        '''Test creating a tag'''
        user = create_user()
        tag = models.Tag.objects.create(
            user=user,
            name='Tag1',
        )

        self.assertEqual(str(tag), tag.name)
