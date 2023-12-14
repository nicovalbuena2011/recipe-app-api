"""
Database models.
"""
from django.conf import settings
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)

class UserManager(BaseUserManager):
    """Manager for users."""
    def create_user(self, email, password = None, **extra_field):
        """Create, save and return a new user"""
        if not email:
            raise ValueError('user must have an email adress.')
        user = self.model(
            email = self.normalize_email(email),
            **extra_field
        )
        user.set_password(password)
        user.save(using = self._db)
        return user
     
    def create_superuser(self, email, password = None, **extra_field):
        """Create an return a new super user."""
        user = self.model(
            email = self.normalize_email(email),
            **extra_field
        )
        user.set_password(password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using = self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """User in the system"""
    email = models.EmailField('email', max_length=50, unique = True)
    name = models.CharField('name', max_length=50)
    is_active = models.BooleanField(default = True)
    is_staff = models.BooleanField(default = False)

    objects = UserManager()

    USERNAME_FIELD = 'email' # Field for aunthentication

class Recipe(models.Model):
    """Recipe object."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete = models.CASCADE,
    )
    title = models.CharField('title', max_length=50)
    description = models.TextField(blank = True)
    time_minutes = models.IntegerField()
    price = models.DecimalField(max_digits = 5, decimal_places = 2)
    link = models.CharField('link', max_length = 50, blank = True)
    tags = models.ManyToManyField('tag')

    ingredients = models.ManyToManyField('Ingredients')

    def __str__(self) -> str:
        return f'{self.title}'
    
class Tag(models.Model):
    """Tag for filtering recipes"""
    name = models.CharField('name', max_length=50)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.name}'
    
class Ingredients(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField('name', max_length=50)

    def __str__(self):
        return f'{self.name}'