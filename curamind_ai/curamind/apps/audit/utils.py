from .models import AuditLog
import logging
logger = logging.getLogger(__name__)

def log_action(user, action, description, ip_address=None, resource=''):
    try:
        AuditLog.objects.create(
            user=user, action=action, description=description,
            ip_address=ip_address, resource=resource,
        )
    except Exception as e:
        logger.error(f"Audit log failed: {e}")
