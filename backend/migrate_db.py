#!/usr/bin/env python3
"""
Database migration script to add all_scores column to documents table
"""

import sqlite3
import os
import json
from datetime import datetime

# Database path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'documents.db')

def migrate_database():
    """Add all_scores column to documents table if it doesn't exist"""
    
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if all_scores column exists
        cursor.execute("PRAGMA table_info(documents)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'all_scores' not in columns:
            print("Adding all_scores column to documents table...")
            cursor.execute("ALTER TABLE documents ADD COLUMN all_scores TEXT")
            conn.commit()
            print("✅ Successfully added all_scores column")
        else:
            print("✅ all_scores column already exists")
        
        # Count documents that need re-classification
        cursor.execute("""
            SELECT COUNT(*) FROM documents 
            WHERE is_classified = 1 AND (all_scores IS NULL OR all_scores = '')
        """)
        count = cursor.fetchone()[0]
        
        if count > 0:
            print(f"📝 Found {count} classified documents without all_scores data")
            print("💡 Tip: Re-classify these documents to get the full ranking data")
        else:
            print("✅ All classified documents have complete data")
            
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    print("🔄 Starting database migration...")
    migrate_database()
    print("✅ Migration completed!")
