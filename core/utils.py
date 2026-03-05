from .models import ActivityLog

def log_action(user, action, message):
    try:
        ActivityLog.objects.create(user=user if user.is_authenticated else None, action=action, message=message)
    except Exception:
        pass
