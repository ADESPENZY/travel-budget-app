from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator, FileExtensionValidator
import re

# Create your models here.
class Account(AbstractUser):
    email = models.EmailField(unique=True)
