import subprocess
from datetime import datetime
from pathlib import Path
from core.logger import get_logger
from core.config import env

logger = get_logger()

STAGING_DIR = Path("/tmp/backup_staging")


def get_latest_remote_file(server, base_path, pattern):
    """
    Resolve latest file on remote server based on:
    - current year
    - filename pattern
    """
    year = datetime.utcnow().year
    remote_dir = f"{base_path}/{year}"

    ssh_user = env("SSH_USER")
    ssh_key = env("SSH_KEY")

    cmd = (
        f"ssh -i {ssh_key} "
        f"{ssh_user}@{server['host']} "
        f"'ls -t {remote_dir}/{pattern} 2>/dev/null | head -n 1'"
    )

    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0 or not result.stdout.strip():
        raise RuntimeError(
            f"No matching file found for pattern {pattern} on {server['name']}"
        )

    return result.stdout.strip()


def collect(server, current_schedule):
    """
    Collect latest files for matching schedule label.
    """
    ssh_user = env("SSH_USER")
    ssh_key = env("SSH_KEY")

    if "dynamic_paths" not in server:
        return

    for item in server["dynamic_paths"]:

        if item["schedule"] != current_schedule:
            continue

        latest_file = get_latest_remote_file(
            server,
            item["base_path"],
            item["pattern"],
        )

        target_dir = STAGING_DIR / server["name"] / item["name"]
        target_dir.mkdir(parents=True, exist_ok=True)

        cmd = [
            "rsync",
            "-az",
            "-e", f"ssh -i {ssh_key}",
            f"{ssh_user}@{server['host']}:{latest_file}",
            str(target_dir),
        ]

        logger.info(
            f"[{server['name']}:{item['name']}] "
            f"Collecting latest file: {latest_file}"
        )

        subprocess.run(cmd, check=True)