"""
Seed organization-level default Risk Acceptability Criteria config (optional).
Run once to create a 'default' org config so reports can use org_default instead of system_draft.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from database import SessionLocal
from models.risk_acceptability_criteria import OrganizationRiskCriteriaConfig
from services.risk_acceptability_criteria_service import (
    SYSTEM_SEVERITY_SCALE,
    SYSTEM_PROBABILITY_SCALE,
    SYSTEM_RISK_MATRIX,
    SYSTEM_DECISION_RULES,
)


def main() -> None:
    db = SessionLocal()
    try:
        existing = db.query(OrganizationRiskCriteriaConfig).filter(
            OrganizationRiskCriteriaConfig.name == "default"
        ).first()
        if existing:
            print("Org config 'default' already exists. Skipping.")
            return
        config = OrganizationRiskCriteriaConfig(
            name="default",
            severity_scale=SYSTEM_SEVERITY_SCALE,
            probability_scale=SYSTEM_PROBABILITY_SCALE,
            risk_matrix=SYSTEM_RISK_MATRIX,
            decision_rules=SYSTEM_DECISION_RULES,
        )
        db.add(config)
        db.commit()
        print("Created organization_risk_criteria_configs 'default' row.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
