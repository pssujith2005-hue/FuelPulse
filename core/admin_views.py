# core/admin_views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import login, get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .models import NewCar
from .forms import NewCarForm

User = get_user_model()

# Helper
def is_admin(user):
    return user.is_active and user.is_superuser

# --- 1. ADMIN LOGIN ---
def admin_login(request):
    if request.user.is_authenticated and request.user.is_superuser:
        return redirect('admin_dashboard')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.is_superuser:
                login(request, user)
                return redirect('admin_dashboard')
            else:
                messages.error(request, "Access Denied. Superuser privileges required.")
    else:
        form = AuthenticationForm()
    return render(request, 'core/admin/login.html', {'form': form})

# --- 2. ADMIN DASHBOARD ---
@login_required
@staff_member_required
def admin_dashboard(request):
    """
    Consolidated Admin Dashboard.
    """
    total_users = User.objects.filter(is_superuser=False).count()
    db_cars_count = NewCar.objects.count()
    
    context = {
        'total_users': total_users,
        'total_db_cars': db_cars_count,
        'suspended_users': User.objects.filter(is_active=False, is_superuser=False).count()
    }
    return render(request, 'core/admin/dashboard.html', context)

# --- 3. CAR CATALOG & VISIBILITY ---
@login_required
@staff_member_required
def car_catalog(request):
    """
    View for viewing and managing the car catalog.
    Note: BUDGET_CARS is imported inside the function to avoid circular imports.
    """
    from .views import BUDGET_CARS
    db_cars = NewCar.objects.all().order_by('-launched_at')
    
    return render(request, 'core/admin/car_catalog.html', {
        'db_cars': db_cars,
        'budget_cars': BUDGET_CARS
    })

@login_required
@staff_member_required
def toggle_car_visibility(request, car_id):
    """
    Toggle car visibility to hide/show from users in recommendations.
    """
    if request.method == 'POST':
        car = get_object_or_404(NewCar, id=car_id)
        car.is_active = not car.is_active
        car.save()
        status = "Live" if car.is_active else "Hidden"
        messages.success(request, f"Market Alert: {car.make} {car.model} is now {status}.")
    return redirect('car_catalog')

@login_required
@staff_member_required
def delete_car_entry(request, car_id):
    """
    Permanently delete a car from the database catalog.
    """
    if request.method == 'POST':
        car = get_object_or_404(NewCar, id=car_id)
        car_name = f"{car.make} {car.model}"
        car.delete()
        messages.error(request, f"System Purge: {car_name} deleted from engine.")
    return redirect('car_catalog')

# --- 4. USER MANAGEMENT ---
@user_passes_test(is_admin, login_url='admin_login')
def manage_users(request):
    """View list of all non-admin users."""
    users = User.objects.filter(is_superuser=False).order_by('-date_joined')
    return render(request, 'core/admin/manage_users.html', {'users': users})

@user_passes_test(is_admin, login_url='admin_login')
def toggle_user_status(request, user_id):
    """Suspends or reactivates a user account."""
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        user.is_active = not user.is_active
        user.save()
        status = "reactivated" if user.is_active else "suspended"
        messages.info(request, f"User {user.username} has been {status}.")
    return redirect('manage_users')

@user_passes_test(is_admin, login_url='admin_login')
def delete_user(request, user_id):
    """Permanently deletes a user."""
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        username = user.username
        user.delete()
        messages.error(request, f"User {username} has been removed from the system.")
    return redirect('manage_users')

# --- 5. ADD NEW CAR ---
@login_required
@staff_member_required
def add_new_car(request):
    if request.method == 'POST':
        form = NewCarForm(request.POST, request.FILES) 
        if form.is_valid():
            form.save()
            messages.success(request, "Market Broadcast Success! Car is now live.")
            return redirect('admin_dashboard')
    else:
        form = NewCarForm()
    return render(request, 'core/admin/add_new_car.html', {'form': form})