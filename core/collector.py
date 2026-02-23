import subprocess
from pathlib import Path
from core.logger import get_logger
from core.config import env

logger = get_logger()

STAGING_DIR = Path("/tmp/backup_staging")

def collect(server):
    ssh_user = env("SSH_USER")
    ssh_key = env("SSH_KEY")

    for path in server["paths"]:
        target = STAGING_DIR / server["name"] / path.lstrip("/")
        target.parent.mkdir(parents=True, exist_ok=True)

        cmd = [
            "rsync",
            "-az",
            "-e", f"ssh -i {ssh_key}",
            f"{ssh_user}@{server['host']}:{path}",
            str(target)
        ]

        logger.info(f"Collecting {path} from {server['name']}")
        subprocess.run(cmd, check=True)