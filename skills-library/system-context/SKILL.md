---
name: system-context
description: Hardware specs, system recovery history, and environment details for the current system
user-invocable: false
---

# System Context

## Hardware

- **Laptop:** ASUS ROG Zephyrus M16 (GU603ZX-XS97)
- **CPU:** Intel i9-12900H
- **GPU:** NVIDIA RTX 3080 Ti
- **RAM:** 32GB
- **SSD:** Samsung 990 Pro 2TB (C:)
- **BIOS:** GU603ZX.311

## System Recovery (December 2025)

The system recovered from a catastrophic SSD failure:
- Old Samsung 2TB died after overheating during Windows Update
- New Samsung 990 Pro 2TB installed
- All applications migrated from D: to C:
- D: drive (dying SSD) physically removed
- BIOS updated to GU603ZX.311
- Secure Boot enabled

**If system issues arise, check the WARRIOR handoffs for detailed history.**

## Database Backups

- `C:\Users\FirstName\Downloads\mongodb_data_backup`
- `C:\Users\FirstName\Downloads\bookcraft_db_backup_16959`

## SessionStart Hook

The `warrior-workflow` plugin includes a SessionStart hook:
1. Runs on: `startup`, `resume`, `clear`, `compact`
2. Location: `C:\Users\<username>\.claude\plugins\warrior-workflow\hooks\`
3. Displays recent handoff files and reminds to read them
