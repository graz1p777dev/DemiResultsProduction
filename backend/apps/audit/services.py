def log_event(*, actor=None, action, entity_type="", entity_id="", ip_address=None, user_agent="", metadata=None):
    from .models import AuditLog

    return AuditLog.objects.create(
        actor=actor,
        action=action,
        entity_type=entity_type,
        entity_id=str(entity_id) if entity_id is not None else "",
        ip_address=ip_address,
        user_agent=user_agent,
        metadata=metadata or {},
    )
