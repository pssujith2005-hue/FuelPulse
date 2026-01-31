# core/context_processors.py
from django.utils import timezone
from datetime import timedelta
from .models import Vehicle, FuelLog, TripLog

def notifications(request):
    if not request.user.is_authenticated:
        return {'notifications': [], 'notification_count': 0}

    alerts = []
    today = timezone.now().date()
    warning_period = today + timedelta(days=7) # Notify 1 week before

    # 1. Fetch User's Active Vehicles
    vehicles = Vehicle.objects.filter(owner=request.user, is_active=True)

    for v in vehicles:
        # --- A. DOCUMENT EXPIRY CHECKS ---
        if v.insurance_expiry and v.insurance_expiry <= warning_period:
            days_left = (v.insurance_expiry - today).days
            if days_left < 0:
                alerts.append({'type': 'danger', 'msg': f"Insurance EXPIRED for {v.model_name} ({v.license_plate})"})
            else:
                alerts.append({'type': 'warning', 'msg': f"Insurance expires in {days_left} days for {v.model_name}"})

        if v.pollution_expiry and v.pollution_expiry <= warning_period:
            days_left = (v.pollution_expiry - today).days
            if days_left < 0:
                alerts.append({'type': 'danger', 'msg': f"PUC EXPIRED for {v.model_name}"})
            else:
                alerts.append({'type': 'warning', 'msg': f"PUC expires in {days_left} days for {v.model_name}"})

        if v.fitness_expiry and v.fitness_expiry <= warning_period:
            days_left = (v.fitness_expiry - today).days
            if days_left < 0:
                alerts.append({'type': 'danger', 'msg': f"Fitness EXPIRED for {v.model_name}"})
            else:
                alerts.append({'type': 'warning', 'msg': f"Fitness expires in {days_left} days for {v.model_name}"})

        # --- B. LOGGING REMINDERS (If no logs for 15+ days) ---
        last_fuel = FuelLog.objects.filter(vehicle=v).order_by('-date').first()
        if not last_fuel or (today - last_fuel.date.date()).days > 15:
            alerts.append({'type': 'info', 'msg': f"Update Fuel Log for {v.model_name} (Last: {last_fuel.date.date() if last_fuel else 'Never'})"})

        last_trip = TripLog.objects.filter(vehicle=v).order_by('-date').first()
        if not last_trip or (today - last_trip.date).days > 7:
            alerts.append({'type': 'info', 'msg': f"Log a trip for {v.model_name}?"})

    # --- C. GENERAL REMINDERS (e.g., Monthly Challan Check) ---
    # Simple logic: Remind on the 1st of every month
    if today.day == 1:
        alerts.append({'type': 'primary', 'msg': "Monthly Check: Verify pending e-Challans for all vehicles."})

    return {
        'notifications': alerts,
        'notification_count': len(alerts)
    }