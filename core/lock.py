import os
import sys

LOCK_FILE = "/tmp/backup_orchestrator.lock"

def acquire_lock():
    if os.path.exists(LOCK_FILE):
        print("Another backup process is running.")
        sys.exit(1)

    with open(LOCK_FILE, "w") as f:
        f.write(str(os.getpid()))

def release_lock():
    if os.path.exists(LOCK_FILE):
        os.remove(LOCK_FILE)