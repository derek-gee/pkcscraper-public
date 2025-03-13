import os
import glob
from utils import log

def cleanup_old_backups(file_path, max_backups=5):
    """Keeps only the last 'max_backups' backups and deletes older ones."""
    backup_pattern = file_path.replace(".xlsx", "_backup_*.xlsx")  # Pattern for backup files
    backup_files = sorted(glob.glob(backup_pattern), key=os.path.getctime)  # Sort by creation time

    # If there are more backups than 'max_backups', delete the oldest ones
    if len(backup_files) > max_backups:
        files_to_delete = backup_files[:-max_backups]  # Keep the latest 'max_backups'
        for file in files_to_delete:
            os.remove(file)
            log(f"Deleted old backup: {file}")
