from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from core import views, admin_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # --- DJANGO ADMIN ---
    path('admin/', admin.site.urls),

    # --- AUTHENTICATION ---
    path('', views.landing_page, name='landing'),
    path('signup/', views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', views.custom_logout_view, name='logout'),
    path('accounts/', include('django.contrib.auth.urls')),

    # --- MAIN DASHBOARD & ANALYTICS ---
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('history/', views.history, name='history'),
    path('reports/', views.reports, name='reports'),
    path('analytics/', views.analytics_dashboard, name='analytics_dashboard'),

    # --- VEHICLE MANAGEMENT ---
    path('add-vehicle/', views.add_vehicle, name='add_vehicle'),
    path('remove-vehicle/<int:vehicle_id>/', views.remove_vehicle, name='remove_vehicle'),
    path('vehicle-stats/<int:vehicle_id>/', views.vehicle_stats, name='vehicle_stats'),
    path('update-maintenance/<int:vehicle_id>/', views.update_maintenance, name='update_maintenance'),
    path('vehicle/update-docs/<int:vehicle_id>/', views.update_vehicle_docs, name='update_vehicle_docs'),

    # --- LOGGING ACTIONS ---
    path('log-trip/', views.log_trip, name='log_trip'),
    path('log-expense/', views.log_expense, name='log_expense'),
    path('log-fuel/<int:vehicle_id>/', views.log_fuel, name='log_fuel'),
    path('delete-history/<str:item_type>/<int:item_id>/', views.delete_history_item, name='delete_history_item'),

    # --- TOOLS & UTILITIES ---
    path('trip-calculator/', views.trip_calculator, name='trip_calculator'),
    path('recommend-car/', views.recommend_car, name='recommend_car'),
    path('car-detail/<str:car_id>/', views.car_detail, name='car_detail'),
    path('calculate-value/', views.calculate_asset_value, name='calculate_value'),
    path('api/chat/', views.chat_with_ai, name='chat_with_ai'),

    # --- USER FLEET TOOLS ---
    path('tools/targets/', views.manage_fleet_targets, name='manage_fleet_targets'),
    path('tools/set-targets/<int:vehicle_id>/', views.set_targets, name='set_targets'),
    path('tools/tco/', views.tco_report, name='tco_report'),
    path('tools/what-if/', views.what_if_analysis, name='what_if_analysis'),

    # --- ADMIN CUSTOM PANEL ---
    path('admin-login/', admin_views.admin_login, name='admin_login'),
    path('admin-panel/', admin_views.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/add-new-car/', admin_views.add_new_car, name='add_new_car'),
    path('admin-panel/catalog/', admin_views.car_catalog, name='car_catalog'),
    path('admin-panel/catalog/toggle/<int:car_id>/', admin_views.toggle_car_visibility, name='toggle_car_visibility'),
    path('admin-panel/catalog/delete/<int:car_id>/', admin_views.delete_car_entry, name='delete_car_entry'),
    
    # --- ADMIN USER MANAGEMENT ---
    path('admin-panel/users/', admin_views.manage_users, name='manage_users'),
    path('admin-panel/users/toggle/<int:user_id>/', admin_views.toggle_user_status, name='toggle_user_status'),
    path('admin-panel/users/delete/<int:user_id>/', admin_views.delete_user, name='delete_user'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)