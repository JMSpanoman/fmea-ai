"""
Script to create a Default Project with example risk reports
Creates a project and generates example reports for each risk report type
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from database import SessionLocal
from models.project import Project
from models.user import User
from models.risk_item import RiskItem
from models.risk_item_version import RiskItemVersion
from models.risk_control import RiskControl
from models.component import Component
from models.risk_management_plan import RiskManagementPlan
from crud import project as project_crud
from crud import user as user_crud
from schemas import project as project_schemas
import uuid
from datetime import datetime

def create_default_project_with_examples():
    """Create Default Project with example risk reports"""
    db: Session = SessionLocal()
    
    try:
        # Get or create a default user
        # Try to find any existing user
        users = db.query(User).limit(1).all()
        if not users:
            # Create a default user if none exists
            default_user = User(
                id=str(uuid.uuid4()),
                auth0_id="default_user",
                email="default@example.com"
            )
            db.add(default_user)
            db.commit()
            db.refresh(default_user)
            user_id = default_user.id
            print(f"✅ Created default user: {default_user.id}")
        else:
            user_id = users[0].id
            print(f"✅ Using existing user: {user_id}")
        
        # Check if Default Project already exists
        existing_project = db.query(Project).filter(
            Project.name == "Default Project",
            Project.user_id == user_id
        ).first()
        
        if existing_project:
            print(f"⚠️  Default Project already exists: {existing_project.id}")
            return existing_project
        
        # Create Default Project
        project_data = project_schemas.ProjectCreate(
            name="Default Project",
            description="Example project with sample risk reports for demonstration"
        )
        
        project = project_crud.create_project(db, project_data, user_id)
        print(f"✅ Created Default Project: {project.id}")
        
        # Create example components
        components = [
            {"name": "Pump", "description": "Main system pump component"},
            {"name": "Valve", "description": "Control valve component"},
            {"name": "Sensor", "description": "Temperature sensor component"}
        ]
        
        created_components = []
        for comp_data in components:
            component = Component(
                id=str(uuid.uuid4()),
                project_id=project.id,
                name=comp_data["name"],
                description=comp_data["description"]
            )
            db.add(component)
            created_components.append(component)
        
        db.commit()
        print(f"✅ Created {len(created_components)} example components")
        
        # Create example risk items
        risk_items_data = [
            {
                "title": "Pump Overpressure Risk",
                "risk_key": "R-001",
                "component_name": "Pump",
                "hazard": "Overpressure",
                "hazardous_situation": "Pump exceeds maximum operating pressure",
                "harm": "System failure, potential injury",
                "severity": 4,
                "probability_of_harm": 3,
                "risk_score": 12,
                "risk_acceptability": "high"
            },
            {
                "title": "Valve Leakage Risk",
                "risk_key": "R-002",
                "component_name": "Valve",
                "hazard": "Leakage",
                "hazardous_situation": "Valve fails to seal properly",
                "harm": "Contamination, system malfunction",
                "severity": 3,
                "probability_of_harm": 2,
                "risk_score": 6,
                "risk_acceptability": "medium"
            },
            {
                "title": "Sensor Failure Risk",
                "risk_key": "R-003",
                "component_name": "Sensor",
                "hazard": "Sensor failure",
                "hazardous_situation": "Sensor provides incorrect readings",
                "harm": "Incorrect system response, potential safety issue",
                "severity": 3,
                "probability_of_harm": 2,
                "risk_score": 6,
                "risk_acceptability": "medium"
            }
        ]
        
        created_risk_items = []
        for risk_data in risk_items_data:
            # Find component
            component = next((c for c in created_components if c.name == risk_data["component_name"]), None)
            
            risk_item = RiskItem(
                id=str(uuid.uuid4()),
                project_id=project.id,
                title=risk_data["title"],
                risk_key=risk_data["risk_key"],
                component_name=risk_data["component_name"],
                component_id=component.id if component else None
            )
            db.add(risk_item)
            db.flush()
            
            # Create initial version
            risk_version = RiskItemVersion(
                id=str(uuid.uuid4()),
                risk_item_id=risk_item.id,
                version_number=1,
                hazard=risk_data["hazard"],
                hazardous_situation=risk_data["hazardous_situation"],
                harm=risk_data["harm"],
                severity=risk_data["severity"],
                probability_of_harm=risk_data["probability_of_harm"],
                risk_score=risk_data["risk_score"],
                risk_acceptability=risk_data["risk_acceptability"],
                residual_severity=risk_data["severity"] - 1 if risk_data["severity"] > 1 else 1,
                residual_probability_of_harm=risk_data["probability_of_harm"] - 1 if risk_data["probability_of_harm"] > 1 else 1,
                residual_risk_score=risk_data["risk_score"] - 3 if risk_data["risk_score"] > 3 else 1
            )
            db.add(risk_version)
            
            # Set as current version
            risk_item.current_version_id = risk_version.id
            
            # Create example risk control
            risk_control = RiskControl(
                id=str(uuid.uuid4()),
                risk_item_id=risk_item.id,
                control_key=f"RC-{risk_item.risk_key.split('-')[1]}",
                control_name=f"Control for {risk_data['title']}",
                control_type="protective",
                control_description=f"Implement protective measures to mitigate {risk_data['hazard']}",
                status="active"
            )
            db.add(risk_control)
            
            created_risk_items.append(risk_item)
        
        db.commit()
        print(f"✅ Created {len(created_risk_items)} example risk items with versions and controls")
        
        # Create example Risk Management Plan
        rmp = RiskManagementPlan(
            id=str(uuid.uuid4()),
            project_id=project.id,
            title="Risk Management Plan – Default Project",
            scope="This Risk Management Plan covers all components in the Default Project including Pump, Valve, and Sensor systems.",
            intended_use="Medical device for demonstration purposes",
            components_json='[{"name": "Pump", "description": "Main system pump"}, {"name": "Valve", "description": "Control valve"}, {"name": "Sensor", "description": "Temperature sensor"}]',
            acceptability_criteria_json='{"thresholds": {"Low": {"min": 1, "max": 7, "acceptability": "acceptable"}, "Medium": {"min": 8, "max": 19, "acceptability": "acceptable_with_justification"}, "High": {"min": 20, "max": 59, "acceptability": "needs_benefit_risk"}, "Critical": {"min": 60, "max": 100, "acceptability": "unacceptable"}}}',
            risk_methodology="Risk score = severity × probability_of_harm",
            review_roles_json='{"risk_manager": "required", "design_lead": "required", "quality_lead": "required"}',
            risk_control_categories_json='["inherent_safety", "protective_measures", "information_for_safety"]',
            benefit_risk_criteria="Benefit-risk analysis required for risks with score ≥ 20",
            lifecycle_linkage="Risk controls trace to Design Inputs/Outputs and V&V tests",
            governance_rules="Human-in-the-loop required for all risk acceptance decisions",
            rendered_html="<html><body><h1>Risk Management Plan</h1><p>Example RMP</p></body></html>",
            status="approved",
            current_version_no=1,
            created_by=user_id
        )
        db.add(rmp)
        db.commit()
        print(f"✅ Created example Risk Management Plan")
        
        print(f"\n✅ Successfully created Default Project with examples!")
        print(f"   Project ID: {project.id}")
        print(f"   Components: {len(created_components)}")
        print(f"   Risk Items: {len(created_risk_items)}")
        print(f"   Risk Management Plan: 1")
        print(f"\n   You can now generate reports:")
        print(f"   - Risk Management Plan (RMP)")
        print(f"   - Risk Management File (RMF)")
        print(f"   - Hazard Analysis")
        print(f"   - Residual Risk Evaluation")
        print(f"   - Risk Control Measures Documentation")
        
        return project
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating default project: {str(e)}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_default_project_with_examples()

