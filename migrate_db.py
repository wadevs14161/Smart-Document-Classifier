#!/usr/bin/env python3
"""
Database migration script to add model columns to existing documents
"""

import sys
import os
sys.path.append('backend')

from sqlalchemy import text
from backend.database import engine, SessionLocal

def migrate_database():
    """Add new model columns to existing database"""
    print("🔄 Starting database migration...")
    
    with engine.connect() as connection:
        # Check if columns exist
        try:
            result = connection.execute(text("SELECT model_used FROM documents LIMIT 1"))
            print("✅ Model columns already exist")
            return
        except Exception:
            print("📝 Adding model columns...")
            
            # Add new columns
            try:
                connection.execute(text("ALTER TABLE documents ADD COLUMN model_used TEXT"))
                connection.execute(text("ALTER TABLE documents ADD COLUMN model_key TEXT"))  
                connection.execute(text("ALTER TABLE documents ADD COLUMN model_id TEXT"))
                connection.commit()
                print("✅ Model columns added successfully")
            except Exception as e:
                print(f"❌ Error adding columns: {e}")
                return False
    
    print("✅ Database migration completed successfully")
    return True

if __name__ == "__main__":
    migrate_database()
