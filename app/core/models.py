"""
Database models.
"""

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
        user = self.model(
            email = self.normalize_email(email),
            **extra_field
        )
        user.set_password(password)
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