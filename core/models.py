from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import datetime

# 1. Custom User
# core/models.py
# core/models.py

class User(AbstractUser):
    is_manager = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=15, blank=True)
    # --- ADD THIS LINE ---
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)

# 2. Vehicle Model (Updated for Dynamic Dropdowns)
class Vehicle(models.Model):
    # Category Choices match the JavaScript keys in add_vehicle.html
    CATEGORY_CHOICES = [
        ('Two Wheeler', 'Two Wheeler'),
        ('Four Wheeler', 'Four Wheeler'),
        ('Heavy Vehicle', 'Heavy Vehicle'),
    ]
    
    ownership_type = models.CharField(max_length=50, default="1st Owner")
    
    FUEL_CHOICES = [
        ('Petrol', 'Petrol'), 
        ('Diesel', 'Diesel'), 
        ('CNG', 'CNG'), 
        ('Electric', 'Electric')
    ]

    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Main Identifiers
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='Four Wheeler')
    make = models.CharField(max_length=50)       # e.g. Maruti, Honda (No restricted choices, accepts JS input)
    model_name = models.CharField(max_length=50) # e.g. Swift, City
    license_plate = models.CharField(max_length=20)
    target_mileage = models.FloatField(default=0.0, help_text="Target km/L (e.g., 18.5)")
    target_cost_per_km = models.FloatField(default=0.0, help_text="Target Cost per KM (e.g., 5.0)")
    purchase_year = models.IntegerField(default=2023)
    purchase_price = models.DecimalField(max_digits=12, decimal_places=2, default=500000.00)
    # Details
    fuel_type = models.CharField(max_length=20, choices=FUEL_CHOICES, default='Petrol')
    current_odometer = models.IntegerField(default=0)
    purchase_price = models.DecimalField(max_digits=12, decimal_places=2, default=500000.00)
    purchase_year = models.IntegerField(default=2021)

    def __str__(self):
        return f"{self.make} {self.model_name}"
    # Document Expiry Dates
    insurance_expiry = models.DateField(null=True, blank=True)
    pollution_expiry = models.DateField(null=True, blank=True)
    fitness_expiry = models.DateField(null=True, blank=True)
    image_url = models.URLField(max_length=500, blank=True, null=True)
    
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.make} {self.model_name} ({self.license_plate})"

# 3. Fuel Log
class FuelLog(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    driver = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now)
    odometer_reading = models.PositiveIntegerField()
    liters_filled = models.DecimalField(max_digits=6, decimal_places=2)
    total_cost = models.DecimalField(max_digits=8, decimal_places=2)
    calculated_km_per_liter = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    calculated_cost_per_km = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.vehicle} - {self.liters_filled}L"

# 4. Trip Log
class TripLog(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    driver = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    start_odometer = models.FloatField()
    end_odometer = models.FloatField()
    distance_km = models.FloatField(editable=False) # Auto-calculated
    
    purpose = models.CharField(max_length=100, choices=[
        ('Business', 'Business'),
        ('Personal', 'Personal'),
        ('Commute', 'Commute'),
        ('Delivery', 'Delivery')
    ], default='Personal')
    
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Auto-calculate distance
        self.distance_km = self.end_odometer - self.start_odometer
        
        # Auto-update Vehicle Odometer if this trip is newer/higher
        if self.end_odometer > self.vehicle.current_odometer:
            self.vehicle.current_odometer = self.end_odometer
            self.vehicle.save()
            
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.vehicle} - {self.distance_km} km"

# 5. Expense Log
class ExpenseLog(models.Model):
    EXPENSE_TYPES = [
        ('Maintenance', 'Maintenance / Service'),
        ('Insurance', 'Insurance'),
        ('Toll', 'Toll / Parking'),
        ('Fine', 'Traffic Fine'),
        ('Cleaning', 'Cleaning / Wash'),
        ('Tax', 'Tax / Registration'),
        ('Accessories', 'Accessories'),
        ('Other', 'Other'),
    ]

    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    expense_type = models.CharField(max_length=50, choices=EXPENSE_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.vehicle} - {self.expense_type} - {self.amount}"

    
# core/models.py

class MaintenanceLog(models.Model):
    SERVICE_CHOICES = [
        ('oil', 'Oil Change'),
        ('tyre', 'Tyre Change'),
        ('general', 'General Service'),
    ]
    
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    service_type = models.CharField(max_length=20, choices=SERVICE_CHOICES)
    date = models.DateField(default=timezone.now)
    odometer_reading = models.IntegerField(help_text="Odometer reading when service was done")
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.get_service_type_display()} - {self.vehicle.license_plate}"

class NewCar(models.Model):
    """Table for admin-added market launches"""
    TYPE_CHOICES = [('Hatchback', 'Hatchback'), ('Sedan', 'Sedan'), ('SUV', 'SUV'), ('EV', 'EV')]
    make = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    car_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    price_lakhs = models.FloatField()
    vehicle_image = models.ImageField(upload_to='new_launches/', null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    launched_at = models.DateTimeField(auto_now_add=True)
    
    # Toggle for recommendation engine visibility
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.make} {self.model}"