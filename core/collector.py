import subprocess
from datetime import datetime
from pathlib import Path
from core.logger import get_logger
from core.config import env

logger = get_logger()

STAGING_DIR = Path("/tmp/backup_staging")


def get_latest_remote_file(server, base_path, pattern):
    current_year = datetime.utcnow().year
    remote_path = f"{base_path}/{current_year}"

    ssh_user = env("SSH_USER")
    ssh_key = env("SSH_KEY")

    cmd = f"ssh -i {ssh_key} {ssh_user}@{server['host']} 'ls -t {remote_path}/{pattern} 2>/dev/null | head -n 1'"

    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    if result.returncode != 0 or not result.stdout.strip():
        raise Exception(f"No matching file found in {remote_path}")

    return result.stdout.strip()


def collect(server):
    ssh_user = env("SSH_USER")
    ssh_key = env("SSH_KEY")

    # dynamic paths
    if "dynamic_paths" in server:
        for item in server["dynamic_paths"]:
            latest_file = get_latest_remote_file(
                server,
                item["base_path"],
                item["pattern"]
            )

            target = STAGING_DIR / server["name"]
            target.mkdir(parents=True, exist_ok=True)

            cmd = [
                "rsync",
                "-az",
                "-e", f"ssh -i {ssh_key}",
                f"{ssh_user}@{server['host']}:{latest_file}",
                str(target)
            ]

            logger.info(f"Collecting latest file {latest_file}")
            subprocess.run(cmd, check=True)