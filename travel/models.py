from django.db import models
from account.models import Account
from django.core.exceptions import ValidationError

# Create your models here.
class Trip(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    trip_name = models.CharField(max_length=100)
    destination_name = models.CharField(max_length=100)  # Allows free-text destination input
    start_date = models.DateField()
    end_date = models.DateField()
    budget = models.DecimalField(max_digits=10, decimal_places=2)

    def total_expenses(self):
        """Calculate the total expenses for the trip."""
        return sum(expense.amount for expense in self.expenses.all())
    
    def total_itineraries(self):
        """Calculate the total itinerary budget for the trip."""
        return sum(item.budget for item in self.items.all())

    def __str__(self):
        return self.trip_name
        
class CategoryBudget(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='category_budgets')  # Link to a trip
    category = models.CharField(max_length=50)  # Name of the category (e.g., Sightseeing)
    budget = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)  # Budget for the category

    def total_expenses(self):
        """Calculate the total amount spent in this category."""
        return sum(expense.amount for expense in self.expenses.all())
    
    def total_itineraries(self):
        """Calculate the total itinerary budget for the category."""
        return sum(item.budget for item in self.itineraries.all())
        
    def remaining_iti_budget(self):
        """Return the remaining budget for the category."""
        return self.budget - self.total_itineraries()

    def remaining_budget(self):
        """Return the remaining budget for the category."""
        return self.budget - self.total_expenses()
    
    def __str__(self):
        if self.trip:
            return f"{self.category} - {self.budget} ({self.trip.trip_name})"
        return f"{self.category} - {self.budget}"

class Itinerary(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='items')
    category_budget = models.ForeignKey(CategoryBudget, on_delete=models.CASCADE, related_name='itineraries')
    title = models.CharField(max_length=100)
    details = models.TextField(blank=True, null=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(blank=True, null=True)
    budget = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def save(self, *args, **kwargs):
        if self.end_time and self.start_time >= self.end_time:
            raise ValueError("End time must be after the start time.")
        if self.budget > self.category_budget.budget:
            raise ValueError("Itinerary budget exceeds the category budget.")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.category_budget.category})"

