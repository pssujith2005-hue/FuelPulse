from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
# IMPORTANT: Import User and all models from your local models
from .models import User, Vehicle, TripLog, FuelLog, ExpenseLog 

from .models import Vehicle

# --- USER AUTH FORMS (UPDATED: Added Phone Number) ---
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control bg-dark text-white border-secondary'}))
    
    class Meta:
        model = User
        fields = ['username', 'email', 'phone_number']

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()
    phone_number = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control bg-dark text-white border-secondary'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'phone_number']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control bg-dark text-white border-secondary', 'readonly': 'readonly'}),
            'email': forms.EmailInput(attrs={'class': 'form-control bg-dark text-white border-secondary'}),
        }



class VehicleForm(forms.ModelForm):
    # 1. Make these optional in the Form Validation
    # (We will handle Make/Model manually in the View)
    make = forms.CharField(required=False)
    model_name = forms.CharField(required=False)
    
    # 2. Make Price optional (It will use the default 500000 from models.py if missing)
    purchase_price = forms.DecimalField(required=False)

    class Meta:
        model = Vehicle
        fields = [
            'category', 
            'make', 
            'model_name', 
            'license_plate', 
            'fuel_type', 
            'ownership_type', 
            'current_odometer', 
            'purchase_year', 
            'purchase_price', # Keep this here, but we made it optional above
            'insurance_expiry', 
            'pollution_expiry', 
            'fitness_expiry'
        ]
        
        widgets = {
            'insurance_expiry': forms.DateInput(attrs={'type': 'date'}),
            'pollution_expiry': forms.DateInput(attrs={'type': 'date'}),
            'fitness_expiry': forms.DateInput(attrs={'type': 'date'}),
        }
# --- TRIP LOG FORM ---
class TripLogForm(forms.ModelForm):
    class Meta:
        model = TripLog
        fields = ['vehicle', 'start_odometer', 'end_odometer', 'date']
        widgets = {
            'vehicle': forms.Select(attrs={'class': 'form-select bg-dark text-white border-secondary'}),
            'start_odometer': forms.NumberInput(attrs={'class': 'form-control bg-dark text-white border-secondary'}),
            'end_odometer': forms.NumberInput(attrs={'class': 'form-control bg-dark text-white border-secondary'}),
            'date': forms.DateInput(attrs={'class': 'form-control bg-dark text-white border-secondary', 'type': 'date'}),
        }

    def __init__(self, user, *args, **kwargs):
        super(TripLogForm, self).__init__(*args, **kwargs)
        self.fields['vehicle'].queryset = Vehicle.objects.filter(owner=user, is_active=True)

# --- EXPENSE LOG FORM ---
class ExpenseLogForm(forms.ModelForm):
    class Meta:
        model = ExpenseLog
        fields = ['vehicle', 'expense_type', 'amount', 'date']
        widgets = {
            'vehicle': forms.Select(attrs={'class': 'form-select bg-dark text-white border-secondary'}),
            'expense_type': forms.Select(attrs={'class': 'form-select bg-dark text-white border-secondary'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control bg-dark text-white border-secondary'}),
            'date': forms.DateInput(attrs={'class': 'form-control bg-dark text-white border-secondary', 'type': 'date'}),
        }

    def __init__(self, user, *args, **kwargs):
        super(ExpenseLogForm, self).__init__(*args, **kwargs)
        self.fields['vehicle'].queryset = Vehicle.objects.filter(owner=user, is_active=True)

# --- CAR RECOMMENDATION FORM ---
class CarRecommendationForm(forms.Form):
    min_price = forms.IntegerField(label='Min Price', required=False, widget=forms.NumberInput(attrs={'class': 'form-control bg-dark text-white border-secondary', 'placeholder': 'e.g. 500000'}))
    max_price = forms.IntegerField(label='Max Price', required=True, widget=forms.NumberInput(attrs={'class': 'form-control bg-dark text-white border-secondary', 'placeholder': 'e.g. 1500000'}))
    vehicle_type = forms.ChoiceField(
        choices=[('Any', 'Any Type'), ('SUV', 'SUV'), ('Sedan', 'Sedan'), ('Hatchback', 'Hatchback'), ('EV', 'Electric Vehicle')],
        widget=forms.Select(attrs={'class': 'form-select bg-dark text-white border-secondary'})
    )

# --- TRIP CALCULATOR FORM ---
class TripCalculatorForm(forms.Form):
    vehicle = forms.ModelChoiceField(
        queryset=Vehicle.objects.none(), 
        label="Select Vehicle",
        widget=forms.Select(attrs={'class': 'form-select bg-dark text-white border-secondary'})
    )
    distance_km = forms.FloatField(
        label="Trip Distance (km)",
        widget=forms.NumberInput(attrs={'class': 'form-control bg-dark text-white border-secondary', 'placeholder': 'e.g. 150'})
    )
    fuel_price = forms.FloatField(
        label="Current Fuel Price (₹/L)",
        widget=forms.NumberInput(attrs={'class': 'form-control bg-dark text-white border-secondary', 'placeholder': 'e.g. 102.5'})
    )
    custom_mileage = forms.FloatField(
        label="Manual Mileage (Optional)",
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control bg-dark text-white border-secondary', 'placeholder': 'Leave empty to use vehicle history'})
    )

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['vehicle'].queryset = Vehicle.objects.filter(owner=user, is_active=True)

# --- FUEL LOG FORM ---
class FuelLogForm(forms.ModelForm):
    class Meta:
        model = FuelLog
        fields = ['odometer_reading', 'liters_filled', 'total_cost', 'date']
        widgets = {
            'odometer_reading': forms.NumberInput(attrs={'class': 'form-control bg-dark text-white border-secondary', 'placeholder': 'e.g. 42650'}),
            'liters_filled': forms.NumberInput(attrs={'class': 'form-control bg-dark text-white border-secondary', 'placeholder': 'e.g. 12.5'}),
            'total_cost': forms.NumberInput(attrs={'class': 'form-control bg-dark text-white border-secondary', 'placeholder': 'e.g. 1500'}),
            'date': forms.DateInput(attrs={'class': 'form-control bg-dark text-white border-secondary', 'type': 'date'}),
        }
# core/forms.py

class ExpenseLogForm(forms.ModelForm):
    # Add the receipt image field here if you want AI scanning later
    receipt_image = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'form-control bg-dark text-white border-secondary'}))

    class Meta:
        model = ExpenseLog
        fields = ['vehicle', 'expense_type', 'amount', 'date', 'receipt_image']
        widgets = {
            'vehicle': forms.Select(attrs={'class': 'form-select bg-dark text-white border-secondary'}),
            'expense_type': forms.Select(attrs={'class': 'form-select bg-dark text-white border-secondary'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control bg-dark text-white border-secondary', 'placeholder': 'e.g. 500'}),
            'date': forms.DateInput(attrs={'class': 'form-control bg-dark text-white border-secondary', 'type': 'date'}),
        }

    # --- THIS IS THE MISSING PART CAUSING THE ERROR ---
    def __init__(self, user, *args, **kwargs):
        super(ExpenseLogForm, self).__init__(*args, **kwargs)
        # Filter vehicles to show only the ones owned by this user
        self.fields['vehicle'].queryset = Vehicle.objects.filter(owner=user, is_active=True)