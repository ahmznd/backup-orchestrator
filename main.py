import sys
import shutil
from core.collector import collect
from core.restic_runner import run_backup, apply_retention
from core.notifier import send_sms
from core.config import load_servers
from core.lock import acquire_lock, release_lock
from core.logger import get_logger

logger = get_logger()

def cleanup():
    shutil.rmtree("/tmp/backup_staging", ignore_errors=True)

def main():
    acquire_lock()

    try:
        servers = load_servers()

        for server in servers:
            collect(server)

        revision = run_backup()
        apply_retention()
        cleanup()

        message = f"""
Backup Completed Successfully

Revision: {revision}
Nodes: {len(servers)}
Status: CLEAN

Central Backup System
"""
        send_sms(message)

    except Exception as e:
        logger.error(str(e))
        send_sms(f"Backup FAILED\nError: {str(e)}")
        cleanup()
        release_lock()
        sys.exit(1)

    release_lock()

if __name__ == "__main__":
    main()