import subprocess
import shutil
from pathlib import Path
from bot.utils.config import DB_PATH

def apply_migrations():
    db_path = Path(DB_PATH)
    migrations_dir = Path("migrations")

    db_path.parent.mkdir(parents=True, exist_ok=True)
    db_path.touch(exist_ok=True)
    print(f"Database file ensured: {db_path}")

    if not migrations_dir.exists():
        print("Migration directory not found!")
        return

    if not shutil.which("sqlite3"):
        print("Please install sqlite3!")
        return

    for migration in sorted(migrations_dir.glob("*.sql")):
        try:
            print(f"Running migration: {migration}")
            command = f"sqlite3 {db_path} < {migration}"
            subprocess.run(command, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error applying migration {migration}: {e}")
            return

    print("All migrations applied successfully.")
