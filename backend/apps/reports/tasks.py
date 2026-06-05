import os
import subprocess
from pathlib import Path

from celery import shared_task
from django.conf import settings
from django.utils import timezone

from .models import ReportExport


@shared_task
def cleanup_old_report_exports(days=30):
    cutoff = timezone.now() - timezone.timedelta(days=days)
    deleted, _ = ReportExport.objects.filter(created_at__lt=cutoff).delete()
    return {"deleted": deleted}


@shared_task
def create_database_backup():
    backup_dir = Path(settings.BACKUP_DIR)
    backup_dir.mkdir(exist_ok=True)
    output_path = backup_dir / f"demiresults-{timezone.now().strftime('%Y%m%d-%H%M%S')}.dump"
    db = settings.DATABASES["default"]
    command = [
        "pg_dump",
        "-h",
        str(db["HOST"]),
        "-p",
        str(db["PORT"]),
        "-U",
        str(db["USER"]),
        "-Fc",
        "-f",
        str(output_path),
        str(db["NAME"]),
    ]
    env = {**os.environ, "PGPASSWORD": str(db["PASSWORD"])}
    subprocess.run(command, env=env, check=True)
    return {"path": str(output_path)}


@shared_task
def cleanup_old_database_backups(days=None):
    retention_days = settings.BACKUP_RETENTION_DAYS if days is None else days
    cutoff = timezone.now() - timezone.timedelta(days=retention_days)
    backup_dir = Path(settings.BACKUP_DIR)
    deleted = 0
    if not backup_dir.exists():
        return {"deleted": deleted}
    for backup_file in backup_dir.glob("demiresults-*.dump"):
        modified_at = timezone.datetime.fromtimestamp(backup_file.stat().st_mtime, tz=timezone.get_current_timezone())
        if modified_at < cutoff:
            backup_file.unlink()
            deleted += 1
    return {"deleted": deleted}
