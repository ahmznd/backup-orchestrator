import subprocess
import uuid
from datetime import datetime
from core.config import env
from core.logger import get_logger

logger = get_logger()

def generate_revision():
    return f"backup-{datetime.utcnow().isoformat()}-{uuid.uuid4().hex[:6]}"

def run_backup():
    revision = generate_revision()

    env_vars = {
        "RESTIC_PASSWORD": env("RESTIC_PASSWORD")
    }

    cmd = [
        "restic",
        "-r", env("RESTIC_REPOSITORY"),
        "backup",
        "/tmp/backup_staging",
        "--tag", revision,
        "--limit-upload", env("RESTIC_LIMIT_UPLOAD", "0"),
        "--limit-download", env("RESTIC_LIMIT_DOWNLOAD", "0")
    ]

    logger.info(f"Starting restic backup: {revision}")
    subprocess.run(cmd, env=env_vars, check=True)

    return revision

def apply_retention():
    cmd = [
        "restic",
        "-r", env("RESTIC_REPOSITORY"),
        "forget",
        "--keep-hourly", env("KEEP_HOURLY"),
        "--keep-daily", env("KEEP_DAILY"),
        "--keep-weekly", env("KEEP_WEEKLY"),
        "--prune"
    ]

    subprocess.run(cmd, check=True)