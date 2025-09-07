#!/usr/bin/env python3
"""
Script om database migratie uit te voeren op Railway productie
"""

import os
import subprocess
import sys

def run_migration():
    """Run database migration"""
    print("🚀 Starting database migration...")
    
    try:
        # Set environment variables for Railway
        env = os.environ.copy()
        
        # Run alembic upgrade
        result = subprocess.run([
            sys.executable, "-m", "alembic", "upgrade", "head"
        ], env=env, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Migration completed successfully!")
            print("Output:", result.stdout)
        else:
            print("❌ Migration failed!")
            print("Error:", result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error running migration: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)
