FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create sample data initialization script with full complex schema
RUN echo '#!/usr/bin/env python3' > /app/init_sample_data.py && \
    echo 'import sqlite3' >> /app/init_sample_data.py && \
    echo 'import datetime' >> /app/init_sample_data.py && \
    echo 'from pathlib import Path' >> /app/init_sample_data.py && \
    echo '' >> /app/init_sample_data.py && \
    echo 'def init_sample_data():' >> /app/init_sample_data.py && \
    echo '    db_path = Path("/app/fmea.db")' >> /app/init_sample_data.py && \
    echo '    conn = sqlite3.connect(str(db_path))' >> /app/init_sample_data.py && \
    echo '    cursor = conn.cursor()' >> /app/init_sample_data.py && \
    echo '    ' >> /app/init_sample_data.py && \
    echo '    # Drop existing tables to ensure clean schema' >> /app/init_sample_data.py && \
    echo '    cursor.execute("DROP TABLE IF EXISTS nonconformance_entries")' >> /app/init_sample_data.py && \
    echo '    cursor.execute("DROP TABLE IF EXISTS change_control_entries")' >> /app/init_sample_data.py && \
    echo '    cursor.execute("DROP TABLE IF EXISTS capa_entries")' >> /app/init_sample_data.py && \
    echo '    cursor.execute("DROP TABLE IF EXISTS fmea_entries")' >> /app/init_sample_data.py && \
    echo '    cursor.execute("DROP TABLE IF EXISTS projects")' >> /app/init_sample_data.py && \
    echo '    cursor.execute("DROP TABLE IF EXISTS users")' >> /app/init_sample_data.py && \
    echo '    ' >> /app/init_sample_data.py && \
    echo '    # Create users table' >> /app/init_sample_data.py && \
    echo '    cursor.execute("""' >> /app/init_sample_data.py && \
    echo '        CREATE TABLE users (' >> /app/init_sample_data.py && \
    echo '            id TEXT PRIMARY KEY,' >> /app/init_sample_data.py && \
    echo '            username TEXT UNIQUE NOT NULL,' >> /app/init_sample_data.py && \
    echo '            email TEXT UNIQUE,' >> /app/init_sample_data.py && \
    echo '            full_name TEXT,' >> /app/init_sample_data.py && \
    echo '            role TEXT DEFAULT "user"' >> /app/init_sample_data.py && \
    echo '        )' >> /app/init_sample_data.py && \
    echo '    """)' >> /app/init_sample_data.py && \
    echo '    ' >> /app/init_sample_data.py && \
    echo '    # Create projects table with full complex schema' >> /app/init_sample_data.py && \
    echo '    cursor.execute("""' >> /app/init_sample_data.py && \
    echo '        CREATE TABLE projects (' >> /app/init_sample_data.py && \
    echo '            id INTEGER PRIMARY KEY AUTOINCREMENT,' >> /app/init_sample_data.py && \
    echo '            user_id TEXT NOT NULL,' >> /app/init_sample_data.py && \
    echo '            name TEXT NOT NULL,' >> /app/init_sample_data.py && \
    echo '            description TEXT,' >> /app/init_sample_data.py && \
    echo '            status TEXT DEFAULT "draft",' >> /app/init_sample_data.py && \
    echo '            version_number TEXT NOT NULL DEFAULT "1.0",' >> /app/init_sample_data.py && \
    echo '            major_version INTEGER NOT NULL DEFAULT 1,' >> /app/init_sample_data.py && \
    echo '            minor_version INTEGER NOT NULL DEFAULT 0,' >> /app/init_sample_data.py && \
    echo '            patch_version INTEGER NOT NULL DEFAULT 0,' >> /app/init_sample_data.py && \
    echo '            version_status TEXT NOT NULL DEFAULT "draft",' >> /app/init_sample_data.py && \
    echo '            version_label TEXT,' >> /app/init_sample_data.py && \
    echo '            change_summary TEXT,' >> /app/init_sample_data.py && \
    echo '            change_details TEXT,' >> /app/init_sample_data.py && \
    echo '            content_hash TEXT,' >> /app/init_sample_data.py && \
    echo '            approval_required TEXT DEFAULT "false",' >> /app/init_sample_data.py && \
    echo '            approved_by TEXT,' >> /app/init_sample_data.py && \
    echo '            approved_at TIMESTAMP,' >> /app/init_sample_data.py && \
    echo '            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,' >> /app/init_sample_data.py && \
    echo '            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,' >> /app/init_sample_data.py && \
    echo '            version_created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,' >> /app/init_sample_data.py && \
    echo '            version_updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP' >> /app/init_sample_data.py && \
    echo '        )' >> /app/init_sample_data.py && \
    echo '    """)' >> /app/init_sample_data.py && \
    echo '    ' >> /app/init_sample_data.py && \
    echo '    # Create fmea_entries table' >> /app/init_sample_data.py && \
    echo '    cursor.execute("""' >> /app/init_sample_data.py && \
    echo '        CREATE TABLE fmea_entries (' >> /app/init_sample_data.py && \
    echo '            id INTEGER PRIMARY KEY AUTOINCREMENT,' >> /app/init_sample_data.py && \
    echo '            project_id INTEGER NOT NULL,' >> /app/init_sample_data.py && \
    echo '            component_name TEXT NOT NULL,' >> /app/init_sample_data.py && \
    echo '            function TEXT,' >> /app/init_sample_data.py && \
    echo '            failure_mode TEXT,' >> /app/init_sample_data.py && \
    echo '            potential_effects TEXT,' >> /app/init_sample_data.py && \
    echo '            severity INTEGER,' >> /app/init_sample_data.py && \
    echo '            potential_causes TEXT,' >> /app/init_sample_data.py && \
    echo '            occurrence INTEGER,' >> /app/init_sample_data.py && \
    echo '            current_controls TEXT,' >> /app/init_sample_data.py && \
    echo '            detection INTEGER,' >> /app/init_sample_data.py && \
    echo '            risk_priority_number INTEGER,' >> /app/init_sample_data.py && \
    echo '            recommended_actions TEXT,' >> /app/init_sample_data.py && \
    echo '            responsibility TEXT,' >> /app/init_sample_data.py && \
    echo '            target_completion_date DATE,' >> /app/init_sample_data.py && \
    echo '            actions_taken TEXT,' >> /app/init_sample_data.py && \
    echo '            final_severity INTEGER,' >> /app/init_sample_data.py && \
    echo '            final_occurrence INTEGER,' >> /app/init_sample_data.py && \
    echo '            final_detection INTEGER,' >> /app/init_sample_data.py && \
    echo '            final_risk_priority_number INTEGER' >> /app/init_sample_data.py && \
    echo '        )' >> /app/init_sample_data.py && \
    echo '    """)' >> /app/init_sample_data.py && \
    echo '    ' >> /app/init_sample_data.py && \
    echo '    # Create capa_entries table' >> /app/init_sample_data.py && \
    echo '    cursor.execute("""' >> /app/init_sample_data.py && \
    echo '        CREATE TABLE capa_entries (' >> /app/init_sample_data.py && \
    echo '            id INTEGER PRIMARY KEY AUTOINCREMENT,' >> /app/init_sample_data.py && \
    echo '            project_id INTEGER NOT NULL,' >> /app/init_sample_data.py && \
    echo '            issue_description TEXT NOT NULL,' >> /app/init_sample_data.py && \
    echo '            source TEXT,' >> /app/init_sample_data.py && \
    echo '            detection_date DATE,' >> /app/init_sample_data.py && \
    echo '            severity TEXT,' >> /app/init_sample_data.py && \
    echo '            root_cause TEXT,' >> /app/init_sample_data.py && \
    echo '            corrective_action TEXT,' >> /app/init_sample_data.py && \
    echo '            preventive_action TEXT,' >> /app/init_sample_data.py && \
    echo '            action_owner TEXT,' >> /app/init_sample_data.py && \
    echo '            due_date DATE,' >> /app/init_sample_data.py && \
    echo '            status TEXT,' >> /app/init_sample_data.py && \
    echo '            effectiveness_check_plan TEXT' >> /app/init_sample_data.py && \
    echo '        )' >> /app/init_sample_data.py && \
    echo '    """)' >> /app/init_sample_data.py && \
    echo '    ' >> /app/init_sample_data.py && \
    echo '    # Create change_control_entries table' >> /app/init_sample_data.py && \
    echo '    cursor.execute("""' >> /app/init_sample_data.py && \
    echo '        CREATE TABLE change_control_entries (' >> /app/init_sample_data.py && \
    echo '            id INTEGER PRIMARY KEY AUTOINCREMENT,' >> /app/init_sample_data.py && \
    echo '            project_id INTEGER NOT NULL,' >> /app/init_sample_data.py && \
    echo '            change_description TEXT NOT NULL,' >> /app/init_sample_data.py && \
    echo '            initiator TEXT,' >> /app/init_sample_data.py && \
    echo '            date_initiated DATE,' >> /app/init_sample_data.py && \
    echo '            status TEXT,' >> /app/init_sample_data.py && \
    echo '            impact_assessment TEXT,' >> /app/init_sample_data.py && \
    echo '            actions_required TEXT,' >> /app/init_sample_data.py && \
    echo '            action_owner TEXT,' >> /app/init_sample_data.py && \
    echo '            due_date DATE,' >> /app/init_sample_data.py && \
    echo '            closure_summary TEXT' >> /app/init_sample_data.py && \
    echo '        )' >> /app/init_sample_data.py && \
    echo '    """)' >> /app/init_sample_data.py && \
    echo '    ' >> /app/init_sample_data.py && \
    echo '    # Create nonconformance_entries table' >> /app/init_sample_data.py && \
    echo '    cursor.execute("""' >> /app/init_sample_data.py && \
    echo '        CREATE TABLE nonconformance_entries (' >> /app/init_sample_data.py && \
    echo '            id INTEGER PRIMARY KEY AUTOINCREMENT,' >> /app/init_sample_data.py && \
    echo '            project_id INTEGER NOT NULL,' >> /app/init_sample_data.py && \
    echo '            issue_description TEXT NOT NULL,' >> /app/init_sample_data.py && \
    echo '            detection_date DATE,' >> /app/init_sample_data.py && \
    echo '            severity TEXT,' >> /app/init_sample_data.py && \
    echo '            root_cause TEXT,' >> /app/init_sample_data.py && \
    echo '            corrective_action TEXT,' >> /app/init_sample_data.py && \
    echo '            preventive_action TEXT,' >> /app/init_sample_data.py && \
    echo '            action_owner TEXT,' >> /app/init_sample_data.py && \
    echo '            due_date DATE,' >> /app/init_sample_data.py && \
    echo '            status TEXT' >> /app/init_sample_data.py && \
    echo '        )' >> /app/init_sample_data.py && \
    echo '    """)' >> /app/init_sample_data.py && \
    echo '    ' >> /app/init_sample_data.py && \
    echo '    # Insert sample users' >> /app/init_sample_data.py && \
    echo '    users_data = [' >> /app/init_sample_data.py && \
    echo '        ("admin-001", "admin", "admin@fmea.com", "System Administrator", "admin"),' >> /app/init_sample_data.py && \
    echo '        ("user-001", "engineer1", "engineer1@fmea.com", "John Engineer", "engineer"),' >> /app/init_sample_data.py && \
    echo '        ("123", "dev-user", "dev@fmea.com", "Development User", "admin")' >> /app/init_sample_data.py && \
    echo '    ]' >> /app/init_sample_data.py && \
    echo '    ' >> /app/init_sample_data.py && \
    echo '    for user in users_data:' >> /app/init_sample_data.py && \
    echo '        cursor.execute("""' >> /app/init_sample_data.py && \
    echo '            INSERT INTO users (id, username, email, full_name, role)' >> /app/init_sample_data.py && \
    echo '            VALUES (?, ?, ?, ?, ?)' >> /app/init_sample_data.py && \
    echo '        """, user)' >> /app/init_sample_data.py && \
    echo '    ' >> /app/init_sample_data.py && \
    echo '    # Insert sample projects with full schema' >> /app/init_sample_data.py && \
    echo '    projects_data = [' >> /app/init_sample_data.py && \
    echo '        ("Default Project", "A comprehensive project with sample FMEA and CAPA data", "123", "active", "1.0", 1, 0, 0, "draft", "Draft", "Initial project setup", "{}", "hash123", "false", None, None),' >> /app/init_sample_data.py && \
    echo '        ("Automotive Brake System", "FMEA analysis for automotive brake components", "engineer1", "active", "2.1", 2, 1, 0, "review", "Review", "Updated brake analysis", "{}", "hash456", "true", "admin", "2025-08-25"),' >> /app/init_sample_data.py && \
    echo '        ("Medical Device FMEA", "Quality analysis for medical device manufacturing", "admin", "draft", "1.0", 1, 0, 0, "draft", "Draft", "Initial setup", "{}", "hash789", "false", None, None)' >> /app/init_sample_data.py && \
    echo '    ]' >> /app/init_sample_data.py && \
    echo '    ' >> /app/init_sample_data.py && \
    echo '    for project in projects_data:' >> /app/init_sample_data.py && \
    echo '        cursor.execute("""' >> /app/init_sample_data.py && \
    echo '            INSERT INTO projects (' >> /app/init_sample_data.py && \
    echo '                name, description, user_id, status, version_number, major_version, minor_version, patch_version,' >> /app/init_sample_data.py && \
    echo '                version_status, version_label, change_summary, change_details, content_hash, approval_required, approved_by, approved_at' >> /app/init_sample_data.py && \
    echo '            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)' >> /app/init_sample_data.py && \
    echo '        """, project)' >> /app/init_sample_data.py && \
    echo '    ' >> /app/init_sample_data.py && \
    echo '    # Get project IDs' >> /app/init_sample_data.py && \
    echo '    cursor.execute("SELECT id FROM projects WHERE name = ?", ("Default Project",))' >> /app/init_sample_data.py && \
    echo '    default_project_id = cursor.fetchone()[0]' >> /app/init_sample_data.py && \
    echo '    ' >> /app/init_sample_data.py && \
    echo '    # Insert sample FMEA data' >> /app/init_sample_data.py && \
    echo '    fmea_data = [' >> /app/init_sample_data.py && \
    echo '        (default_project_id, "Brake Pads", "Provide friction surface", "Excessive wear", "Reduced braking performance", 8, "Aggressive driving", 6, "Regular inspection", 4, 192, "Replace pads", "Maintenance Team", "2025-12-31", "", 8, 3, 4, 96),' >> /app/init_sample_data.py && \
    echo '        (default_project_id, "Brake Rotors", "Provide contact surface", "Warping", "Vibration during braking", 7, "Overheating", 5, "Temperature monitoring", 4, 140, "Replace rotors", "Service Team", "2025-12-31", "", 7, 4, 4, 112),' >> /app/init_sample_data.py && \
    echo '        (default_project_id, "Hydraulic System", "Transmit brake force", "Fluid contamination", "Reduced performance", 7, "Moisture ingress", 4, "Fluid analysis", 3, 84, "Replace fluid", "Maintenance Team", "2025-12-31", "", 7, 3, 3, 63)' >> /app/init_sample_data.py && \
    echo '    ]' >> /app/init_sample_data.py && \
    echo '    ' >> /app/init_sample_data.py && \
    echo '    for entry in fmea_data:' >> /app/init_sample_data.py && \
    echo '        cursor.execute("""' >> /app/init_sample_data.py && \
    echo '            INSERT INTO fmea_entries (' >> /app/init_sample_data.py && \
    echo '                project_id, component_name, function, failure_mode, potential_effects,' >> /app/init_sample_data.py && \
    echo '                severity, potential_causes, occurrence, current_controls, detection,' >> /app/init_sample_data.py && \
    echo '                risk_priority_number, recommended_actions, responsibility, target_completion_date,' >> /app/init_sample_data.py && \
    echo '                actions_taken, final_severity, final_occurrence, final_detection, final_risk_priority_number' >> /app/init_sample_data.py && \
    echo '            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)' >> /app/init_sample_data.py && \
    echo '        """, entry)' >> /app/init_sample_data.py && \
    echo '    ' >> /app/init_sample_data.py && \
    echo '    # Insert sample CAPA data' >> /app/init_sample_data.py && \
    echo '    capa_data = [' >> /app/init_sample_data.py && \
    echo '        (default_project_id, "Brake pad wear exceeds specifications", "Quality Control", "2025-08-20", "High", "Insufficient material quality", "Replace with higher grade material", "Implement supplier quality audit", "Procurement Team", "2025-09-30", "In Progress", "Monthly wear rate monitoring"),' >> /app/init_sample_data.py && \
    echo '        (default_project_id, "Rotor surface finish issues", "Manufacturing", "2025-08-18", "Medium", "Tool wear in machining", "Replace cutting tools", "Implement preventive maintenance schedule", "Production Team", "2025-09-15", "Completed", "Surface finish measurement"),' >> /app/init_sample_data.py && \
    echo '        (default_project_id, "Hydraulic fluid contamination", "Maintenance", "2025-08-15", "High", "Poor sealing system", "Replace seals and flush system", "Improve seal design", "Engineering Team", "2025-10-15", "In Progress", "Fluid quality testing")' >> /app/init_sample_data.py && \
    echo '    ]' >> /app/init_sample_data.py && \
    echo '    ' >> /app/init_sample_data.py && \
    echo '    for entry in capa_data:' >> /app/init_sample_data.py && \
    echo '        cursor.execute("""' >> /app/init_sample_data.py && \
    echo '        INSERT INTO capa_entries (' >> /app/init_sample_data.py && \
    echo '            project_id, issue_description, source, detection_date, severity, root_cause,' >> /app/init_sample_data.py && \
    echo '            corrective_action, preventive_action, action_owner, due_date, status, effectiveness_check_plan' >> /app/init_sample_data.py && \
    echo '        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)' >> /app/init_sample_data.py && \
    echo '        """, entry)' >> /app/init_sample_data.py && \
    echo '    ' >> /app/init_sample_data.py && \
    echo '    # Insert sample Change Control data' >> /app/init_sample_data.py && \
    echo '    change_control_data = [' >> /app/init_sample_data.py && \
    echo '        (default_project_id, "Update brake pad material specification", "Engineering", "2025-08-22", "In Progress", "Improve wear resistance", "Update design documents", "Design Team", "2025-09-30", "Material specification updated"),' >> /app/init_sample_data.py && \
    echo '        (default_project_id, "Modify rotor cooling system", "R&D", "2025-08-21", "Approved", "Reduce thermal stress", "Implement new cooling design", "R&D Team", "2025-10-15", "Cooling system redesigned")' >> /app/init_sample_data.py && \
    echo '    ]' >> /app/init_sample_data.py && \
    echo '    ' >> /app/init_sample_data.py && \
    echo '    for entry in change_control_data:' >> /app/init_sample_data.py && \
    echo '        cursor.execute("""' >> /app/init_sample_data.py && \
    echo '            INSERT INTO change_control_entries (' >> /app/init_sample_data.py && \
    echo '                project_id, change_description, initiator, date_initiated, status, impact_assessment,' >> /app/init_sample_data.py && \
    echo '                actions_required, action_owner, due_date, closure_summary' >> /app/init_sample_data.py && \
    echo '            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)' >> /app/init_sample_data.py && \
    echo '        """, entry)' >> /app/init_sample_data.py && \
    echo '    ' >> /app/init_sample_data.py && \
    echo '    # Insert sample Non-Conformance data' >> /app/init_sample_data.py && \
    echo '    nonconformance_data = [' >> /app/init_sample_data.py && \
    echo '        (default_project_id, "Brake pad thickness below specification", "2025-08-19", "High", "Manufacturing process variation", "Adjust manufacturing parameters", "Implement statistical process control", "Production Team", "2025-09-20", "In Progress"),' >> /app/init_sample_data.py && \
    echo '        (default_project_id, "Rotor surface finish out of spec", "2025-08-17", "Medium", "Tool wear", "Replace cutting tools", "Implement tool life monitoring", "Maintenance Team", "2025-09-10", "Completed")' >> /app/init_sample_data.py && \
    echo '    ]' >> /app/init_sample_data.py && \
    echo '    ' >> /app/init_sample_data.py && \
    echo '    for entry in nonconformance_data:' >> /app/init_sample_data.py && \
    echo '        cursor.execute("""' >> /app/init_sample_data.py && \
    echo '            INSERT INTO nonconformance_entries (' >> /app/init_sample_data.py && \
    echo '                project_id, issue_description, detection_date, severity, root_cause,' >> /app/init_sample_data.py && \
    echo '                corrective_action, preventive_action, action_owner, due_date, status' >> /app/init_sample_data.py && \
    echo '            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)' >> /app/init_sample_data.py && \
    echo '        """, entry)' >> /app/init_sample_data.py && \
    echo '    ' >> /app/init_sample_data.py && \
    echo '    conn.commit()' >> /app/init_sample_data.py && \
    echo '    conn.close()' >> /app/init_sample_data.py && \
    echo '    print("Complex database schema with sample data initialized successfully!")' >> /app/init_sample_data.py && \
    echo '' >> /app/init_sample_data.py && \
    echo 'if __name__ == "__main__":' >> /app/init_sample_data.py && \
    echo '    init_sample_data()' >> /app/init_sample_data.py

# Make the script executable
RUN chmod +x /app/init_sample_data.py

# Initialize sample data
RUN python /app/init_sample_data.py

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
