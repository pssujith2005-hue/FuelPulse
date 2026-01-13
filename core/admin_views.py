# core/admin_views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth import get_user_model

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
                messages.error(request, "Access Denied.")
    else:
        form = AuthenticationForm()
    return render(request, 'core/admin/login.html', {'form': form})

# --- 2. ADMIN DASHBOARD (User Mgmt Only) ---
@user_passes_test(is_admin, login_url='admin_login')
def admin_dashboard(request):
    total_users = User.objects.filter(is_superuser=False).count()
    suspended_users = User.objects.filter(is_active=False).count()
    return render(request, 'core/admin/dashboard.html', {
        'total_users': total_users,
        'suspended_users': suspended_users
    })

# --- 3. USER MANAGEMENT ACTIONS ---
@user_passes_test(is_admin, login_url='admin_login')
def manage_users(request):
    users = User.objects.filter(is_superuser=False).order_by('-date_joined')
    return render(request, 'core/admin/manage_users.html', {'users': users})

@user_passes_test(is_admin, login_url='admin_login')
def toggle_user_status(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if user.is_active:
        user.is_active = False
        messages.warning(request, f"User {user.username} suspended.")
    else:
        user.is_active = True
        messages.success(request, f"User {user.username} reactivated.")
    user.save()
    return redirect('manage_users')

@user_passes_test(is_admin, login_url='admin_login')
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.delete()
    messages.error(request, "User account deleted.")
    return redirect('manage_users')