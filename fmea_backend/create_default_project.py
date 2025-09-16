#!/usr/bin/env python3
"""
Script to create a default project in the FMEA database
"""

import sqlite3
import datetime
from pathlib import Path

def create_default_project():
    """Create a default project in the database"""
    
    # Database path - use the same path as the main application
    db_path = Path(__file__).parent / "fmea.db"
    
    # Connect to database
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    try:
        # Create projects table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                user_id TEXT NOT NULL,
                status TEXT DEFAULT 'draft',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Check if default project already exists
        cursor.execute("SELECT * FROM projects WHERE name = ?", ("Default Project",))
        existing_project = cursor.fetchone()
        
        if existing_project:
            print("✅ Default Project already exists!")
            print(f"  - ID: {existing_project[0]}")
            print(f"  - Name: {existing_project[1]}")
            print(f"  - Description: {existing_project[2]}")
            print(f"  - User ID: {existing_project[3]}")
            print(f"  - Status: {existing_project[4]}")
            return
        
        # Create default project
        cursor.execute("""
            INSERT INTO projects (name, description, user_id, status)
            VALUES (?, ?, ?, ?)
        """, ("Default Project", "A default project to get you started with FMEA analysis. This project includes sample data to help you understand how to use the system.", "dev-user", "active"))
        
        project_id = cursor.lastrowid
        
        # Commit the changes
        conn.commit()
        
        print(f"✅ Default Project created successfully!")
        print(f"  - ID: {project_id}")
        print(f"  - Name: Default Project")
        print(f"  - Description: A default project to get you started with FMEA analysis. This project includes sample data to help you understand how to use the system.")
        print(f"  - User ID: dev-user")
        print(f"  - Status: active")
        
    except Exception as e:
        print(f"❌ Error creating default project: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    print("Creating Default Project...")
    create_default_project()
    print("Done!") 