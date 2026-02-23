# Backup Orchestrator

Enterprise-grade centralized backup automation system.

## Features

- Multi-node file collection
- Encrypted backups via Restic
- Bandwidth throttling
- Structured logging
- SMS notification
- Retention policy

## Architecture

[4 Source Servers] → [Central Node] → [Encrypted Remote Repository]

## Tech Stack

- Python 3
- Restic
- Rsync
- Twilio or other notifying system

## Security

- SSH key-based auth
- Encrypted repository
- Environment-based secrets