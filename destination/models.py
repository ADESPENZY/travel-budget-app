from django.db import models
from django.utils.text import slugify
from django.utils import timezone
from travel.models import Trip
# Create your models here.

class Country(models.Model):
    COUNTRY_CHOICES = [
    ('Argentina', 'Argentina'),
    ('Brazil', 'Brazil'),
    ('Chile', 'Chile'),
    ('Colombia', 'Colombia'),
    ('Mexico', 'Mexico'),
    ('Peru', 'Peru'),
    ('Russia', 'Russia'),
    ('United States', 'United States'), 
    ('Sweden', 'Sweden'),
    ('Norway', 'Norway'),
    ('Finland', 'Finland'),
    ('Denmark', 'Denmark'),
    ('Switzerland', 'Switzerland'),
    ('Austria', 'Austria'),
    ('Belgium', 'Belgium'),
    ('Netherlands', 'Netherlands'),
    ('Portugal', 'Portugal'),
    ('Iceland', 'Iceland'),
    ('Philippines', 'Philippines'),
    ('Vietnam', 'Vietnam'),
    ('United Arab Emirates', 'United Arab Emirates'),
    ('Saudi Arabia', 'Saudi Arabia'),
    ('Canada', 'Canada'),
]
    country  = models.CharField(choices=COUNTRY_CHOICES, max_length=30)

    def __str__(self):
      return self.country
    
class Destination(models.Model):
    location_name = models.CharField(max_length=100)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    slug = models.SlugField(unique=True, max_length=255, blank=True, null=True)
    description = models.TextField(max_length=1000)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='destination_image',)
    created_at = models.DateTimeField(default=timezone.now,)
    is_popular = models.BooleanField(default=False)
    
    def __str__ (self):
        return self.location_name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.location_name)
            print(f"Generated slug: {self.slug}")  # Debugging line
        super().save(*args, **kwargs)