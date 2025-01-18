from django.db import models
from django.conf import settings
from travel.models import Trip, CategoryBudget
from django.core.exceptions import ValidationError

class Expense(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='expenses')
    category = models.ForeignKey(CategoryBudget, on_delete=models.CASCADE, related_name='expenses')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='expenses')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255)
    date = models.DateField(auto_now_add=True)
    receipt = models.FileField(upload_to='expense_receipts/', blank=True, null=True)

    def clean(self):
        
        # Validate file type for receipt
        if self.receipt:
            allowed_types = [
                'image/jpeg', 'image/png', 'application/pdf',
                'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            ]
            if self.receipt.file.content_type not in allowed_types:
                raise ValidationError("Only image, PDF, or Word document files are allowed.")


    def __str__(self):
        return f"{self.description} - {self.amount} for {self.trip}"
