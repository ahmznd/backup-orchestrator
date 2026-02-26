import sys
import shutil
from core.collector import collect
from core.restic_runner import run_backup, apply_retention
from core.notifier import send_sms
from core.config import load_servers
from core.lock import acquire_lock, release_lock
from core.logger import get_logger

logger = get_logger()

STAGING_DIR = "/tmp/backup_staging"


def cleanup():
    shutil.rmtree(STAGING_DIR, ignore_errors=True)


def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py <hourly|daily|weekly>")
        sys.exit(1)

    current_schedule = sys.argv[1]

    acquire_lock()

    try:
        servers = load_servers()

        logger.info(f"Starting backup for schedule: {current_schedule}")

        for server in servers:
            collect(server, current_schedule)

        revision = run_backup()
        apply_retention()
        cleanup()

        message = f"""
Backup Completed Successfully

Schedule: {current_schedule}
Revision: {revision}
Nodes: {len(servers)}
Status: CLEAN

Central Backup System
"""
        send_sms(message)

    except Exception as e:
        logger.exception("Backup failed")
        send_sms(f"Backup FAILED\nSchedule: {current_schedule}\nError: {str(e)}")
        cleanup()
        release_lock()
        sys.exit(1)

    release_lock()


if __name__ == "__main__":
    main()