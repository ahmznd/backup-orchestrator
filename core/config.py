import os
import yaml
from dotenv import load_dotenv

load_dotenv("config/.env")

def env(key, default=None):
    return os.getenv(key, default)

def load_servers():
    with open("config/servers.yaml") as f:
        return yaml.safe_load(f)["servers"]