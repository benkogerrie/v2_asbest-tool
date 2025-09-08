#!/usr/bin/env python3
"""
Script om de description migratie uit te voeren op productie
"""

import os
import subprocess
import sys

def run_migration():
    """Run the description migration"""
    print("Running description migration...")
    
    try:
        # Run alembic upgrade
        result = subprocess.run([
            sys.executable, "-m", "alembic", "upgrade", "head"
        ], capture_output=True, text=True, check=True)
        
        print("✅ Migration successful!")
        print("Output:", result.stdout)
        
        if result.stderr:
            print("Warnings:", result.stderr)
            
    except subprocess.CalledProcessError as e:
        print("❌ Migration failed!")
        print("Error:", e.stderr)
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    
    return True

def check_migration_status():
    """Check current migration status"""
    print("Checking migration status...")
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "alembic", "current"
        ], capture_output=True, text=True, check=True)
        
        print("Current migration status:")
        print(result.stdout)
        
    except subprocess.CalledProcessError as e:
        print("❌ Failed to check status!")
        print("Error:", e.stderr)
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def main():
    print("=== Description Migration Script ===")
    print()
    
    # Check current status
    check_migration_status()
    print()
    
    # Run migration
    if run_migration():
        print()
        print("=== Migration Complete ===")
        print("The description field should now be available in the prompts table.")
        print("Try updating a prompt description in the UI to test.")
    else:
        print()
        print("=== Migration Failed ===")
        print("Please check the error messages above.")

if __name__ == "__main__":
    main()
