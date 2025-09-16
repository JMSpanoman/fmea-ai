#!/usr/bin/env python3
import sqlite3
import datetime
from pathlib import Path

def init_database():
    db_path = Path("/app/db/fmea.db")
    
    # Remove existing database to start fresh
    if db_path.exists():
        db_path.unlink()
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute("""
        CREATE TABLE users (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE,
            full_name TEXT,
            role TEXT DEFAULT "user"
        )
    """)
    
    # Create projects table with full schema matching the SQLAlchemy model
    cursor.execute("""
        CREATE TABLE projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT "draft",
            version_number TEXT NOT NULL DEFAULT "1.0",
            major_version INTEGER NOT NULL DEFAULT 1,
            minor_version INTEGER NOT NULL DEFAULT 0,
            patch_version INTEGER NOT NULL DEFAULT 0,
            version_status TEXT NOT NULL DEFAULT "draft",
            version_label TEXT,
            change_summary TEXT,
            change_details TEXT,
            content_hash TEXT,
            approval_required TEXT DEFAULT "false",
            approved_by TEXT,
            approved_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            version_created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            version_updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create fmea_entries table
    cursor.execute("""
        CREATE TABLE fmea_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            component_name TEXT NOT NULL,
            function TEXT,
            failure_mode TEXT,
            potential_effects TEXT,
            severity INTEGER,
            potential_causes TEXT,
            occurrence INTEGER,
            current_controls TEXT,
            detection INTEGER,
            risk_priority_number INTEGER,
            recommended_actions TEXT,
            responsibility TEXT,
            target_completion_date DATE,
            actions_taken TEXT,
            final_severity INTEGER,
            final_occurrence INTEGER,
            final_detection INTEGER,
            final_risk_priority_number INTEGER
        )
    """)
    
    # Create capa_entries table
    cursor.execute("""
        CREATE TABLE capa_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            issue_description TEXT NOT NULL,
            source TEXT,
            detection_date DATE,
            severity TEXT,
            root_cause TEXT,
            corrective_action TEXT,
            preventive_action TEXT,
            action_owner TEXT,
            due_date DATE,
            status TEXT,
            effectiveness_check_plan TEXT
        )
    """)
    
    # Create change_control_entries table
    cursor.execute("""
        CREATE TABLE change_control_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            change_description TEXT NOT NULL,
            initiator TEXT,
            date_initiated DATE,
            status TEXT,
            impact_assessment TEXT,
            actions_required TEXT,
            action_owner TEXT,
            due_date DATE,
            closure_summary TEXT
        )
    """)
    
    # Create nonconformance_entries table
    cursor.execute("""
        CREATE TABLE nonconformance_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            issue_description TEXT NOT NULL,
            detection_date DATE,
            severity TEXT,
            root_cause TEXT,
            corrective_action TEXT,
            preventive_action TEXT,
            action_owner TEXT,
            due_date DATE,
            status TEXT
        )
    """)
    
    # Insert sample users
    users_data = [
        ("123", "dev-user", "dev@fmea.com", "Development User", "admin"),
    ]
    
    for user in users_data:
        cursor.execute("""
            INSERT INTO users (id, username, email, full_name, role)
            VALUES (?, ?, ?, ?, ?)
        """, user)
    
    # Insert sample projects with full schema
    projects_data = [
        ("Project 1", "First FMEA project for analysis and quality management", "123", "active", "1.0", 1, 0, 0, "draft", "Draft", "Initial project setup", "{}", "hash123", "false", None, None),
        ("Project 2", "Second FMEA project for analysis and quality management", "123", "active", "1.0", 1, 0, 0, "draft", "Draft", "Initial project setup", "{}", "hash456", "false", None, None),
        ("Project 3", "Third FMEA project for comprehensive risk assessment", "123", "active", "1.0", 1, 0, 0, "draft", "Draft", "Initial project setup", "{}", "hash789", "false", None, None),
    ]
    
    for project in projects_data:
        cursor.execute("""
            INSERT INTO projects (
                name, description, user_id, status, version_number, major_version, minor_version, patch_version,
                version_status, version_label, change_summary, change_details, content_hash, approval_required, approved_by, approved_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, project)
    
    conn.commit()
    conn.close()
    print("Database initialized successfully with full schema and sample data!")

if __name__ == "__main__":
    init_database()
