from django.db import models
from userAccount.models import Account
from django.core.validators import RegexValidator, FileExtensionValidator

# Create your models here.
class User_Profile(models.Model):
    CURRENCY_CHOICES = [
        ('USD', 'US Dollar'),
        ('EUR', 'Euro'),
        ('GBP', 'British Pound'),
        ('JPY', 'Japanese Yen'),
        ('AUD', 'Australian Dollar'),
        ('CAD', 'Canadian Dollar'),
        ('CHF', 'Swiss Franc'),
        ('CNY', 'Chinese Yuan'),
        ('SEK', 'Swedish Krona'),
        ('NZD', 'New Zealand Dollar'),
        ('MXN', 'Mexican Peso'),
        ('SGD', 'Singapore Dollar'),
        ('HKD', 'Hong Kong Dollar'),
        ('NOK', 'Norwegian Krone'),
        ('KRW', 'South Korean Won'),
        ('TRY', 'Turkish Lira'),
        ('INR', 'Indian Rupee'),
        ('RUB', 'Russian Ruble'),
        ('ZAR', 'South African Rand'),
        ('BRL', 'Brazilian Real'),
        ('THB', 'Thai Baht'),
        ('MYR', 'Malaysian Ringgit'),
        ('IDR', 'Indonesian Rupiah'),
        ('PHP', 'Philippine Peso'),
        ('VND', 'Vietnamese Dong'),
        ('ILS', 'Israeli Shekel'),
        ('PLN', 'Polish Zloty'),
        ('AED', 'United Arab Emirates Dirham'),
        ('SAR', 'Saudi Riyal'),
        ('EGP', 'Egyptian Pound'),
        ('PKR', 'Pakistani Rupee'),
        ('BDT', 'Bangladeshi Taka'),
        ('NGN', 'Nigerian Naira'),
        ('KWD', 'Kuwaiti Dinar'),
    ]
    
    TRAVEL_PREFERENCES = (
        ('adventure', 'Adventure'),
        ('relaxation', 'Relaxation'),
        ('culture', 'Culture'),
        ('nature', 'Nature'),
        ('luxury', 'Luxury'),
        ('others', 'Others')
    )
     
    TRAVEL_FREQUENCY_CHOICES = (
        ('frequent', 'Frequent (Monthly)'),
        ('occasional', 'Occasional (Quarterly)'),
        ('rare', 'Rare (Yearly)'),
    )
    
    user = models.OneToOneField(Account, on_delete=models.CASCADE, related_name='profile')
    firstname = models.CharField(max_length=255, null=True, blank=True)
    lastname = models.CharField(max_length=255, null=True, blank=True)
    dob = models.DateField(null=True, blank=True)
    bio = models.TextField( blank=True, null=True)
    preferred_currency = models.CharField(max_length=10, choices=CURRENCY_CHOICES, default='USD', blank=True, null=True)
    travel_preferences = models.CharField(max_length=20, choices=TRAVEL_PREFERENCES, blank=True, null=True)
    travel_frequency = models.CharField(max_length=20, choices=TRAVEL_FREQUENCY_CHOICES, blank=True, null=True)
    image = models.ImageField(upload_to='profile_image', validators=[FileExtensionValidator(['png', 'jpg', 'jpeg'])], blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(
        max_length=15, 
        blank=True, 
        null=True
    )
    favorite_destinations = models.TextField(blank=True, null=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True, null=True)
    emergency_contact_phone = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )
    
    complete_profile = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}'s Profile"

   
    

    
