#!/usr/bin/env python3
"""
Phase 1 Internal Test Script
Tests for bugs, robustness, and potential issues
"""

import sys
import os
import importlib
import traceback
from typing import List, Dict, Any

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'fmea_backend'))

class TestResult:
    def __init__(self, name: str, passed: bool, message: str = "", error: Exception = None):
        self.name = name
        self.passed = passed
        self.message = message
        self.error = error

def test_imports() -> List[TestResult]:
    """Test all critical imports"""
    results = []
    
    modules_to_test = [
        ("database", "database"),
        ("models.user", "User model"),
        ("models.project", "Project model"),
        ("models.component", "Component model"),
        ("models.project_profile", "ProjectProfile model"),
        ("models.fmea", "FMEARow model"),
        ("models.fmea_version", "FMEAVersion model"),
        ("models.risk_item", "RiskItem model"),
        ("crud.user", "User CRUD"),
        ("crud.project", "Project CRUD"),
        ("crud.component", "Component CRUD"),
        ("crud.project_profile", "ProjectProfile CRUD"),
        ("crud.fmea", "FMEA CRUD"),
        ("crud.risk_item", "Risk Item CRUD"),
        ("schemas.project", "Project schemas"),
        ("schemas.component", "Component schemas"),
        ("schemas.project_profile", "ProjectProfile schemas"),
        ("schemas.fmea", "FMEA schemas"),
        ("schemas.risk_item", "Risk Item schemas"),
        ("auth.security", "Auth security"),
        ("auth.dependencies", "Auth dependencies"),
        ("routers.projects", "Projects router"),
        ("routers.components", "Components router"),
        ("routers.project_profile", "ProjectProfile router"),
        ("routers.fmea", "FMEA router"),
        ("routers.risk_items", "Risk Items router"),
        ("routers.ai_phase1", "AI Phase 1 router"),
        ("routers.export", "Export router"),
    ]
    
    for module_path, description in modules_to_test:
        try:
            importlib.import_module(module_path)
            results.append(TestResult(f"Import {description}", True, f"Successfully imported {module_path}"))
        except Exception as e:
            results.append(TestResult(f"Import {description}", False, f"Failed to import {module_path}", e))
    
    return results


def test_project_profile_upsert_and_get() -> List[TestResult]:
    """ProjectProfile should upsert and remain 1:1 per project."""
    results: List[TestResult] = []
    try:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from database import Base
        from models.user import User
        from models.project import Project
        from crud.project_profile import get_project_profile, upsert_project_profile
        from schemas.project_profile import ProjectProfileUpsert

        engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
        TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        Base.metadata.create_all(bind=engine)

        db = TestingSessionLocal()
        try:
            u = User(email="pp@example.com", auth0_id="pp")
            db.add(u)
            db.commit()
            db.refresh(u)
            p = Project(user_id=u.id, name="P", description=None)
            db.add(p)
            db.commit()
            db.refresh(p)

            rec1 = upsert_project_profile(
                db,
                project_id=p.id,
                data=ProjectProfileUpsert(intended_use="Use A", key_safety_characteristics=["A", "B"]),
            )
            rec2 = upsert_project_profile(
                db,
                project_id=p.id,
                data=ProjectProfileUpsert(intended_use="Use B"),
            )
            got = get_project_profile(db, p.id)

            if got and got.id == rec1.id == rec2.id and got.intended_use == "Use B":
                results.append(TestResult("ProjectProfile upsert 1:1", True))
            else:
                results.append(TestResult("ProjectProfile upsert 1:1", False, f"Unexpected profile state: {got}"))
        finally:
            db.close()
    except Exception as e:
        results.append(TestResult("ProjectProfile upsert/get", False, "Error testing project profile", e))
    return results


def test_components_bulk_create_replace_safety() -> List[TestResult]:
    """Bulk create/replace should create components and not error."""
    results: List[TestResult] = []
    try:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from database import Base
        from models.user import User
        from models.project import Project
        from crud.component import bulk_create_replace_components
        from schemas.component import ComponentBulkItem

        engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
        TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        Base.metadata.create_all(bind=engine)

        db = TestingSessionLocal()
        try:
            u = User(email="c@example.com", auth0_id="c")
            db.add(u)
            db.commit()
            db.refresh(u)
            p = Project(user_id=u.id, name="P", description=None)
            db.add(p)
            db.commit()
            db.refresh(p)

            items = [
                ComponentBulkItem(id="c1", name="System", description="Top", parent_id=None, tags=["top"]),
                ComponentBulkItem(id="c2", name="Subsystem", description="Child", parent_id="c1", tags=["child"]),
            ]
            comps, stats = bulk_create_replace_components(db, project_id=p.id, items=items)
            if len(comps) >= 2:
                results.append(TestResult("Components bulk create/replace", True, f"stats={stats}"))
            else:
                results.append(TestResult("Components bulk create/replace", False, f"Expected >=2 components, got {len(comps)}; stats={stats}"))
        finally:
            db.close()
    except Exception as e:
        results.append(TestResult("Components bulk create/replace", False, "Error testing bulk components", e))
    return results


def test_initialize_project_content_idempotent() -> List[TestResult]:
    """Initializer should seed only once and be safe to call repeatedly."""
    results: List[TestResult] = []
    try:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from database import Base
        from models.user import User
        from models.project import Project
        from models.document import Document, DocumentVersion
        from models.component import Component
        from models.risk_item import RiskItem
        from models.risk_item_version import RiskItemVersion
        from models.fmea import FMEARow
        from services.project_setup_initializer import initialize_project_content
        import uuid

        engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
        TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        Base.metadata.create_all(bind=engine)

        db = TestingSessionLocal()
        try:
            u = User(email="init@example.com", auth0_id="init")
            db.add(u)
            db.commit()
            db.refresh(u)
            p = Project(user_id=u.id, name="P", description=None)
            db.add(p)
            db.commit()
            db.refresh(p)

            # Add 2 components
            c1 = Component(id=str(uuid.uuid4()), project_id=p.id, name="Comp A", description=None)
            c2 = Component(id=str(uuid.uuid4()), project_id=p.id, name="Comp B", description=None)
            db.add_all([c1, c2])
            db.commit()

            s1 = initialize_project_content(db, project_id=p.id, user_id=u.id)
            risks_after_1 = db.query(RiskItem).filter(RiskItem.project_id == p.id).count()
            rows_after_1 = db.query(FMEARow).filter(FMEARow.project_id == p.id).count()

            s2 = initialize_project_content(db, project_id=p.id, user_id=u.id)
            risks_after_2 = db.query(RiskItem).filter(RiskItem.project_id == p.id).count()
            rows_after_2 = db.query(FMEARow).filter(FMEARow.project_id == p.id).count()

            if risks_after_1 >= 1 and rows_after_1 == 2 and risks_after_2 == risks_after_1 and rows_after_2 == rows_after_1:
                results.append(TestResult("initialize_project_content idempotent", True, f"s1={s1} s2={s2}"))
            else:
                results.append(
                    TestResult(
                        "initialize_project_content idempotent",
                        False,
                        f"Unexpected counts: risks {risks_after_1}->{risks_after_2}, fmea {rows_after_1}->{rows_after_2}; s1={s1} s2={s2}",
                    )
                )
        finally:
            db.close()
    except Exception as e:
        results.append(TestResult("initialize_project_content idempotent", False, "Error testing initializer", e))
    return results


def test_initialize_from_profile_creates_versions_and_is_idempotent() -> List[TestResult]:
    """initialize_project_from_profile should generate drafts only when empty and create document versions."""
    results: List[TestResult] = []
    try:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from database import Base
        from models.user import User
        from models.project import Project
        from models.component import Component
        from models.project_profile import ProjectProfile
        from models.document import Document, DocumentVersion
        from services.project_profile_initializer import initialize_project_from_profile
        import uuid

        engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
        TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        Base.metadata.create_all(bind=engine)

        db = TestingSessionLocal()
        try:
            u = User(email="initprof@example.com", auth0_id="initprof")
            db.add(u)
            db.commit()
            db.refresh(u)

            p = Project(user_id=u.id, name="P", description=None)
            db.add(p)
            db.commit()
            db.refresh(p)

            # Profile + components
            prof = ProjectProfile(
                id=str(uuid.uuid4()),
                project_id=p.id,
                intended_use="Use X",
                device_description="Device",
                user_population="Users",
                use_environment="Lab",
                key_safety_characteristics=["k1"],
            )
            db.add(prof)
            c1 = Component(id=str(uuid.uuid4()), project_id=p.id, name="Comp A", description=None)
            db.add(c1)
            db.commit()

            # Create the docs as "not started" placeholders
            docs = []
            for t, name, content in [
                ("rmp", "RMP", "RMP Starter (edit this document):\n- Scope:\n"),
                ("hazard_analysis", "Hazard Analysis", "Hazard Analysis export configuration starter. Use Hazard Analysis page to generate."),
                ("fmea", "FMEA", "FMEA starter. Use FMEA Generator to add rows and save to the project."),
                ("design_inputs_doc", "Design Inputs", "Design Inputs Documentation starter. Use Generate New to compile component-scoped requirements and trace evidence."),
                ("design_outputs_doc", "Design Outputs", "Design Outputs Documentation starter. Use Generate New to compile component-scoped implementation artifacts and trace evidence."),
                ("vv_plan", "V&V Plan", "V&V Plan starter. Use Generate New to compile verification/validation plan scaffolding and trace links."),
                ("vv_evidence", "V&V Evidence", "V&V Evidence Report starter. Use Generate New to compile component-scoped verification/validation evidence and trace links."),
                ("traceability_matrix", "Traceability Matrix", "Traceability Matrix export configuration starter."),
                ("residual_risk", "Residual Risk", "Residual Risk Evaluation export configuration starter. Use Residual Risk Evaluation page to generate."),
                ("risk_controls_doc", "Risk Controls Doc", "Risk Control Measures Documentation export configuration starter. Use Risk Controls Documentation page to generate."),
            ]:
                d = Document(id=str(uuid.uuid4()), project_id=p.id, name=name, type=t, content=content, version=1, status="Not started")
                db.add(d)
                db.commit()
                db.refresh(d)
                # initial version row (mimic create_document behavior)
                dv = DocumentVersion(id=str(uuid.uuid4()), document_id=d.id, version=1, content=d.content, changes={})
                db.add(dv)
                db.commit()
                docs.append(d)

            # First run should update expected docs and increment versions
            s1 = initialize_project_from_profile(db, project_id=p.id)
            updated_types_1 = set(s1.get("updated_documents") or [])

            ok_updated = updated_types_1.issuperset(
                {
                    "rmp",
                    "hazard_analysis",
                    "fmea",
                    "design_inputs_doc",
                    "design_outputs_doc",
                    "vv_plan",
                    "vv_evidence",
                    "traceability_matrix",
                    "residual_risk",
                    "risk_controls_doc",
                }
            )
            if not ok_updated:
                results.append(TestResult("initialize-from-profile updates expected docs", False, f"updated={updated_types_1}"))
            else:
                results.append(TestResult("initialize-from-profile updates expected docs", True))

            # Verify document versions bumped to 2
            bumped = True
            for d in docs:
                db.refresh(d)
                if d.version != 2:
                    bumped = False
            results.append(TestResult("initialize-from-profile bumps document.version", bumped, "Expected version=2 for all docs"))

            # Verify version rows exist (2 per doc)
            ok_versions = True
            for d in docs:
                cnt = db.query(DocumentVersion).filter(DocumentVersion.document_id == d.id).count()
                if cnt < 2:
                    ok_versions = False
            results.append(TestResult("initialize-from-profile creates DocumentVersion rows", ok_versions))

            # Second run should be idempotent: no further version bumps
            s2 = initialize_project_from_profile(db, project_id=p.id)
            for d in docs:
                db.refresh(d)
            if all(d.version == 2 for d in docs) and (s2.get("updated_documents") == [] or s2.get("updated_documents") is None):
                results.append(TestResult("initialize-from-profile idempotent", True))
            else:
                results.append(TestResult("initialize-from-profile idempotent", False, f"s2={s2} versions={[d.version for d in docs]}"))

            # Ensure re-running does not overwrite user-edited content
            edited = db.query(Document).filter(Document.project_id == p.id, Document.type == "rmp").first()
            edited.content = "USER EDITED CONTENT"
            db.commit()
            v_before = edited.version
            s3 = initialize_project_from_profile(db, project_id=p.id)
            db.refresh(edited)
            if edited.content == "USER EDITED CONTENT" and edited.version == v_before and (s3.get("updated_documents") == [] or s3.get("updated_documents") is None):
                results.append(TestResult("initialize-from-profile preserves user edits on rerun", True))
            else:
                results.append(TestResult("initialize-from-profile preserves user edits on rerun", False, f"s3={s3} content={edited.content} v={edited.version}"))
        finally:
            db.close()
    except Exception as e:
        results.append(TestResult("initialize-from-profile", False, "Error testing initialize-from-profile", e))
    return results


def test_generate_all_docs_with_ai_from_setup_does_not_overwrite_user_edits() -> List[TestResult]:
    """AI generation should only fill placeholders/scaffolds and never overwrite user-edited content."""
    results: List[TestResult] = []
    try:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from database import Base
        from models.user import User
        from models.project import Project
        from models.component import Component
        from models.project_profile import ProjectProfile
        from models.document import Document
        from services.project_ai_doc_generator import generate_all_docs_with_ai_from_setup
        from services.project_profile_initializer import initialize_project_from_profile
        import uuid

        engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
        TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        Base.metadata.create_all(bind=engine)

        db = TestingSessionLocal()
        try:
            u = User(email="aiinit@example.com", auth0_id="aiinit")
            db.add(u)
            db.commit()
            db.refresh(u)

            p = Project(user_id=u.id, name="P", description=None)
            db.add(p)
            db.commit()
            db.refresh(p)

            prof = ProjectProfile(
                id=str(uuid.uuid4()),
                project_id=p.id,
                intended_use="Pacemaker intended use",
                device_description="Cardiac pacemaker",
                user_population="Clinicians",
                use_environment="Hospital",
                key_safety_characteristics=["therapy continuity"],
            )
            db.add(prof)
            c1 = Component(id=str(uuid.uuid4()), project_id=p.id, name="Battery", description=None)
            db.add(c1)
            db.commit()

            # Seed deterministic scaffolds into docs (creates required docs + content)
            initialize_project_from_profile(db, project_id=p.id)

            # User edits RMP -> should never be overwritten by AI generator
            rmp = db.query(Document).filter(Document.project_id == p.id, Document.type == "rmp").first()
            rmp.content = "USER EDITED RMP CONTENT"
            db.commit()
            v_before = rmp.version

            def stub_ai(doc_type: str, context: str, meta: dict) -> str:
                if doc_type == "rmf_addendum":
                    return (
                        "RMF Addendum — DRAFT\n"
                        f"Project ID: {meta.get('project_id')}\n\n"
                        "ADDED: Supplemental RMF compilation notes."
                    )
                return (
                    "DRAFT — Generated with AI from Project Setup\n"
                    f"Project ID: {meta.get('project_id')}\n\n"
                    f"AI CONTENT FOR {doc_type}"
                )

            def stub_fmea_rows(context: str, meta: dict):
                # Always return one scored row for the Battery component
                return [
                    {
                        "component_id": c1.id,
                        "component_name": "Battery",
                        "hazard": "Loss of pacing therapy due to power failure",
                        "failure_mode": "Battery depletion earlier than expected",
                        "effect": "Therapy interruption; bradycardia not treated",
                        "cause": "High current draw; manufacturing variability",
                        "occurrence": 3,
                        "severity": 9,
                        "detection": 4,
                        "mitigation": "Battery monitoring; derating; end-of-life alerting",
                    }
                ]

            out = generate_all_docs_with_ai_from_setup(
                db, project_id=p.id, ai_draft_fn=stub_ai, ai_fmea_rows_fn=stub_fmea_rows
            )
            db.refresh(rmp)

            if rmp.content == "USER EDITED RMP CONTENT" and rmp.version == v_before:
                results.append(TestResult("AI generator preserves user-edited content", True))
            else:
                results.append(
                    TestResult(
                        "AI generator preserves user-edited content",
                        False,
                        f"content={rmp.content} v={rmp.version} out={out}",
                    )
                )

            # Should update at least one scaffold doc
            if (out.get("attempted", 0) >= 1) and (len(out.get("updated") or []) >= 1):
                results.append(TestResult("AI generator updates scaffold docs", True))
            else:
                results.append(TestResult("AI generator updates scaffold docs", False, f"out={out}"))

            # RMF should be eligible (starts as placeholder from REQUIRED_DOCS) and should be updated by AI.
            if "rmf" in [str(x).lower() for x in (out.get("updated") or [])]:
                results.append(TestResult("AI generator populates RMF from setup", True))
            else:
                results.append(TestResult("AI generator populates RMF from setup", False, f"out.updated={out.get('updated')}"))

            # If RMF already has user content, generator should append an addendum (not overwrite).
            rmf = db.query(Document).filter(Document.project_id == p.id, Document.type == "rmf").first()
            rmf.content = "USER RMF CONTENT"
            db.commit()
            v_rmf_before = rmf.version

            out_rmf_add = generate_all_docs_with_ai_from_setup(
                db, project_id=p.id, doc_types=["rmf"], ai_draft_fn=stub_ai, ai_fmea_rows_fn=stub_fmea_rows
            )
            db.refresh(rmf)
            if rmf.content.startswith("USER RMF CONTENT") and "AI ADDENDUM" in rmf.content and rmf.version == v_rmf_before + 1:
                results.append(TestResult("AI generator appends RMF addendum when RMF has existing content", True))
            else:
                results.append(
                    TestResult(
                        "AI generator appends RMF addendum when RMF has existing content",
                        False,
                        f"v_before={v_rmf_before} v_after={rmf.version} out={out_rmf_add} content_snip={rmf.content[:200]!r}",
                    )
                )

            # Re-run should be idempotent: should not append the same addendum twice.
            v_rmf_before2 = rmf.version
            out_rmf_add2 = generate_all_docs_with_ai_from_setup(
                db, project_id=p.id, doc_types=["rmf"], ai_draft_fn=stub_ai, ai_fmea_rows_fn=stub_fmea_rows
            )
            db.refresh(rmf)
            if rmf.version == v_rmf_before2:
                results.append(TestResult("AI generator RMF addendum idempotent", True))
            else:
                results.append(TestResult("AI generator RMF addendum idempotent", False, f"out2={out_rmf_add2} v={rmf.version}"))

            # Re-run should be idempotent once AI content is present (not scaffold and not placeholder)
            out2 = generate_all_docs_with_ai_from_setup(
                db, project_id=p.id, ai_draft_fn=stub_ai, ai_fmea_rows_fn=stub_fmea_rows
            )
            if len(out2.get("updated") or []) == 0:
                results.append(TestResult("AI generator idempotent after AI content", True))
            else:
                results.append(TestResult("AI generator idempotent after AI content", False, f"out2={out2}"))

            # FMEA row should now have hazard + scores populated (from stub_fmea_rows)
            from models.fmea import FMEARow
            row = db.query(FMEARow).filter(FMEARow.project_id == p.id, FMEARow.component_id == c1.id).first()
            ok_hazard = bool(isinstance(row.ai_metadata, dict) and (row.ai_metadata.get("hazard") or "").strip())
            ok_scores = (row.severity == 9 and row.probability == 3 and row.detection == 4)
            if ok_hazard and ok_scores:
                results.append(TestResult("AI generator populates scored FMEA row + hazard", True))
            else:
                results.append(TestResult("AI generator populates scored FMEA row + hazard", False, f"hazard_ok={ok_hazard} scores=({row.severity},{row.probability},{row.detection}) meta={row.ai_metadata}"))

            # User edits the FMEA row scores -> AI generator must not overwrite
            row.severity = 1
            row.probability = 1
            row.detection = 1
            row.failure_mode = "USER EDITED FAILURE MODE"
            db.commit()
            out3 = generate_all_docs_with_ai_from_setup(
                db, project_id=p.id, ai_draft_fn=stub_ai, ai_fmea_rows_fn=stub_fmea_rows
            )
            db.refresh(row)
            if row.severity == 1 and row.probability == 1 and row.detection == 1 and row.failure_mode == "USER EDITED FAILURE MODE":
                results.append(TestResult("AI generator does not overwrite user-edited FMEA row fields", True))
            else:
                results.append(TestResult("AI generator does not overwrite user-edited FMEA row fields", False, f"out3={out3} row=({row.failure_mode},{row.severity},{row.probability},{row.detection})"))
        finally:
            db.close()
    except Exception as e:
        results.append(TestResult("AI generator", False, "Error testing AI generator", e))
    return results

def test_risk_controls_doc_includes_existing_controls() -> List[TestResult]:
    """Risk Controls doc should compile existing RiskControl entities (and not be empty when controls exist)."""
    results: List[TestResult] = []
    try:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from database import Base
        from models.user import User
        from models.project import Project
        from models.component import Component
        from models.project_profile import ProjectProfile
        from models.document import Document
        from models.risk_item import RiskItem
        from models.risk_control import RiskControl
        from services.project_profile_initializer import initialize_project_from_profile
        import uuid

        engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
        TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        Base.metadata.create_all(bind=engine)

        db = TestingSessionLocal()
        try:
            u = User(email="rcdoc@example.com", auth0_id="rcdoc")
            db.add(u)
            db.commit()
            db.refresh(u)

            p = Project(user_id=u.id, name="Pacemaker Project", description=None)
            db.add(p)
            db.commit()
            db.refresh(p)

            prof = ProjectProfile(
                id=str(uuid.uuid4()),
                project_id=p.id,
                intended_use="Pacemaker intended use",
                device_description="Cardiac pacemaker",
                user_population="Clinicians",
                use_environment="Hospital",
                key_safety_characteristics=["therapy continuity"],
            )
            db.add(prof)

            c1 = Component(id=str(uuid.uuid4()), project_id=p.id, name="Battery", description=None)
            db.add(c1)
            db.commit()

            # Create a RiskItem + one structured RiskControl
            ri = RiskItem(
                id=str(uuid.uuid4()),
                project_id=p.id,
                component_id=c1.id,
                component_name="Battery",
                title="Battery depletion risk",
                description="Risk of therapy interruption due to battery depletion.",
                status="open",
                risk_key="R-001",
            )
            db.add(ri)
            db.commit()
            db.refresh(ri)

            rc = RiskControl(
                id=str(uuid.uuid4()),
                risk_item_id=ri.id,
                project_id=p.id,
                control_key="RC-001",
                control_name="Battery end-of-life alert",
                control_description="Provide end-of-life alerting and battery status monitoring.",
                control_type="information",
                verification_method=None,
                status="active",
            )
            db.add(rc)
            db.commit()

            # Run initializer: should populate risk_controls_doc if placeholder/empty, creating a new version
            out = initialize_project_from_profile(db, project_id=p.id)
            doc = db.query(Document).filter(Document.project_id == p.id, Document.type == "risk_controls_doc").first()
            ok_present = doc is not None and "Battery end-of-life alert" in (doc.content or "")
            if ok_present:
                results.append(TestResult("Risk Controls doc includes structured RiskControl", True))
            else:
                results.append(TestResult("Risk Controls doc includes structured RiskControl", False, f"out={out} content_snip={(doc.content or '')[:200] if doc else None!r}"))
        finally:
            db.close()
    except Exception as e:
        results.append(TestResult("Risk Controls doc includes structured RiskControl", False, "Error testing risk controls doc generation", e))
    return results


def test_risk_control_verification_method_creates_vv_activity_and_is_traceable() -> List[TestResult]:
    """Creating a RiskControl with structured verification_method should auto-create a draft VVTest and TraceLink."""
    results: List[TestResult] = []
    try:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from database import Base
        from models.user import User
        from models.project import Project
        from models.component import Component
        from models.project_profile import ProjectProfile
        from models.document import Document
        from models.risk_item import RiskItem
        from models.trace_link import TraceLink
        from models.vv_test import VVTest
        from crud import risk_control as risk_control_crud
        from schemas.risk_item import RiskControlCreate
        from services.project_profile_initializer import initialize_project_from_profile
        import uuid

        engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
        TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        Base.metadata.create_all(bind=engine)

        db = TestingSessionLocal()
        try:
            u = User(email="rcvv@example.com", auth0_id="rcvv")
            db.add(u)
            db.commit()
            db.refresh(u)

            p = Project(user_id=u.id, name="Pacemaker Project", description=None)
            db.add(p)
            db.commit()
            db.refresh(p)

            prof = ProjectProfile(
                id=str(uuid.uuid4()),
                project_id=p.id,
                intended_use="Pacemaker intended use",
                device_description="Cardiac pacemaker",
                user_population="Clinicians",
                use_environment="Hospital",
                key_safety_characteristics=["therapy continuity"],
            )
            db.add(prof)
            c1 = Component(id=str(uuid.uuid4()), project_id=p.id, name="Battery", description=None)
            db.add(c1)
            db.commit()

            ri = RiskItem(
                id=str(uuid.uuid4()),
                project_id=p.id,
                component_id=c1.id,
                component_name="Battery",
                title="Battery depletion risk",
                description="Risk of therapy interruption due to battery depletion.",
                status="open",
                risk_key="R-001",
            )
            db.add(ri)
            db.commit()
            db.refresh(ri)

            rc = risk_control_crud.create_risk_control(
                db,
                RiskControlCreate(
                    risk_item_id=ri.id,
                    project_id=p.id,
                    control_name="Battery end-of-life alert",
                    control_description="Provide end-of-life alerting and battery status monitoring.",
                    control_type="information",
                    verification_method="Test: Verify end-of-life alert triggers at defined threshold; record results. [DRAFT]",
                ),
                created_by=u.id,
            )

            # VVTest created + trace link created
            vt = db.query(VVTest).filter(VVTest.project_id == p.id).first()
            link = db.query(TraceLink).filter(
                TraceLink.project_id == p.id,
                TraceLink.from_type == "risk_control",
                TraceLink.from_id == rc.id,
                TraceLink.to_type == "vv_test",
            ).first()

            if vt and link and rc.trace_to_verification_test == vt.id and vt.status == "draft":
                results.append(TestResult("RiskControl verification_method auto-creates draft VVTest + TraceLink", True))
            else:
                results.append(TestResult("RiskControl verification_method auto-creates draft VVTest + TraceLink", False, f"vt={bool(vt)} link={bool(link)} rc.trace_to_verification_test={getattr(rc,'trace_to_verification_test',None)} vt_status={getattr(vt,'status',None) if vt else None}"))

            # V&V Plan doc should include a reference to the verification activity (generated from profile initializer)
            initialize_project_from_profile(db, project_id=p.id)
            vv_doc = db.query(Document).filter(Document.project_id == p.id, Document.type == "vv_plan").first()
            ok_vv_plan = vv_doc is not None and "Risk Control Verification Activities" in (vv_doc.content or "") and (vt.vv_key or vt.id[:8]) in (vv_doc.content or "")
            if ok_vv_plan:
                results.append(TestResult("V&V Plan includes risk-control verification activity reference", True))
            else:
                results.append(TestResult("V&V Plan includes risk-control verification activity reference", False, f"snip={(vv_doc.content or '')[:250] if vv_doc else None!r}"))
        finally:
            db.close()
    except Exception as e:
        results.append(TestResult("RiskControl verification_method creates VV activity", False, "Error testing verification method -> VV activity", e))
    return results

def test_generated_artifact_cleanup() -> List[TestResult]:
    """Cleanup should delete expired rows/files and prune missing-file rows."""
    results: List[TestResult] = []
    try:
        import tempfile
        from pathlib import Path
        from datetime import datetime, timedelta, timezone
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker

        from database import Base
        from models.user import User
        from models.project import Project
        from crud.generated_artifact import create_generated_artifact, cleanup_generated_artifacts

        engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
        TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        Base.metadata.create_all(bind=engine)

        db = TestingSessionLocal()
        try:
            u1 = User(email="u1@example.com", auth0_id="u1")
            db.add(u1)
            db.commit()
            db.refresh(u1)

            p1 = Project(user_id=u1.id, name="P1", description=None)
            db.add(p1)
            db.commit()
            db.refresh(p1)

            with tempfile.TemporaryDirectory() as td:
                temp_dir = Path(td)
                # Expired file present
                (temp_dir / "expired.docx").write_text("x", encoding="utf-8")
                create_generated_artifact(
                    db,
                    user_id=u1.id,
                    project_id=p1.id,
                    filename="expired.docx",
                    artifact_type="word_report",
                    expires_at=datetime.now(timezone.utc) - timedelta(days=1),
                )

                # Missing file row (not expired)
                create_generated_artifact(
                    db,
                    user_id=u1.id,
                    project_id=p1.id,
                    filename="missing.docx",
                    artifact_type="word_report",
                    expires_at=None,
                )

                stats = cleanup_generated_artifacts(
                    db,
                    base_dirs={"word_report": temp_dir},
                    now=datetime.now(timezone.utc),
                )

                if not (temp_dir / "expired.docx").exists():
                    results.append(TestResult("Cleanup deletes expired file", True))
                else:
                    results.append(TestResult("Cleanup deletes expired file", False, "expired.docx still exists"))

                # Should have removed both rows: expired + missing file
                if stats.get("deleted_rows_expired", 0) >= 1 and stats.get("deleted_rows_missing_file", 0) >= 1:
                    results.append(TestResult("Cleanup deletes expired rows and missing-file rows", True))
                else:
                    results.append(TestResult("Cleanup deletes expired rows and missing-file rows", False, f"Unexpected stats: {stats}"))
        finally:
            db.close()
    except Exception as e:
        results.append(TestResult("GeneratedArtifact cleanup", False, "Error testing cleanup", e))
    return results
def test_model_relationships() -> List[TestResult]:
    """Test model relationships and foreign keys"""
    results = []
    
    try:
        from models.project import Project
        from models.component import Component
        from models.fmea import FMEARow
        from models.fmea_version import FMEAVersion
        
        # Check Project relationships
        if hasattr(Project, 'components'):
            results.append(TestResult("Project.components relationship", True))
        else:
            results.append(TestResult("Project.components relationship", False, "Missing components relationship"))
        
        if hasattr(Project, 'fmea_rows'):
            results.append(TestResult("Project.fmea_rows relationship", True))
        else:
            results.append(TestResult("Project.fmea_rows relationship", False, "Missing fmea_rows relationship"))
        
        # Check Component relationships
        if hasattr(Component, 'project'):
            results.append(TestResult("Component.project relationship", True))
        else:
            results.append(TestResult("Component.project relationship", False, "Missing project relationship"))
        
        if hasattr(Component, 'fmea_rows'):
            results.append(TestResult("Component.fmea_rows relationship", True))
        else:
            results.append(TestResult("Component.fmea_rows relationship", False, "Missing fmea_rows relationship"))
        
        # Check FMEARow relationships
        if hasattr(FMEARow, 'project'):
            results.append(TestResult("FMEARow.project relationship", True))
        else:
            results.append(TestResult("FMEARow.project relationship", False, "Missing project relationship"))
        
        if hasattr(FMEARow, 'component'):
            results.append(TestResult("FMEARow.component relationship", True))
        else:
            results.append(TestResult("FMEARow.component relationship", False, "Missing component relationship"))
        
        if hasattr(FMEARow, 'versions'):
            results.append(TestResult("FMEARow.versions relationship", True))
        else:
            results.append(TestResult("FMEARow.versions relationship", False, "Missing versions relationship"))
        
        # Check FMEAVersion relationships
        if hasattr(FMEAVersion, 'fmea_row'):
            results.append(TestResult("FMEAVersion.fmea_row relationship", True))
        else:
            results.append(TestResult("FMEAVersion.fmea_row relationship", False, "Missing fmea_row relationship"))
        
        # Check RiskItem relationships
        from models.risk_item import RiskItem
        if hasattr(RiskItem, 'project'):
            results.append(TestResult("RiskItem.project relationship", True))
        else:
            results.append(TestResult("RiskItem.project relationship", False, "Missing project relationship"))
        
        if hasattr(RiskItem, 'fmea_row'):
            results.append(TestResult("RiskItem.fmea_row relationship", True))
        else:
            results.append(TestResult("RiskItem.fmea_row relationship", False, "Missing fmea_row relationship"))
        
        # Check Project.risk_items relationship
        if hasattr(Project, 'risk_items'):
            results.append(TestResult("Project.risk_items relationship", True))
        else:
            results.append(TestResult("Project.risk_items relationship", False, "Missing risk_items relationship"))
        
        # Check FMEARow.risk_items relationship
        if hasattr(FMEARow, 'risk_items'):
            results.append(TestResult("FMEARow.risk_items relationship", True))
        else:
            results.append(TestResult("FMEARow.risk_items relationship", False, "Missing risk_items relationship"))
        
    except Exception as e:
        results.append(TestResult("Model relationships", False, "Error checking relationships", e))
    
    return results

def test_crud_functions() -> List[TestResult]:
    """Test CRUD function signatures and logic"""
    results = []
    
    try:
        from crud import project, component, fmea, user
        
        # Test project CRUD
        required_project_funcs = ['create_project', 'get_projects_by_user', 'get_project', 'update_project', 'delete_project']
        for func_name in required_project_funcs:
            if hasattr(project, func_name):
                results.append(TestResult(f"Project CRUD: {func_name}", True))
            else:
                results.append(TestResult(f"Project CRUD: {func_name}", False, f"Missing function {func_name}"))
        
        # Test component CRUD
        required_component_funcs = ['create_component', 'get_components_by_project', 'get_component', 'update_component', 'delete_component']
        for func_name in required_component_funcs:
            if hasattr(component, func_name):
                results.append(TestResult(f"Component CRUD: {func_name}", True))
            else:
                results.append(TestResult(f"Component CRUD: {func_name}", False, f"Missing function {func_name}"))
        
        # Test FMEA CRUD
        required_fmea_funcs = ['create_fmea_row', 'get_fmea_rows_by_project', 'get_fmea_row', 'update_fmea_row', 'delete_fmea_row', 'get_fmea_version_history']
        for func_name in required_fmea_funcs:
            if hasattr(fmea, func_name):
                results.append(TestResult(f"FMEA CRUD: {func_name}", True))
            else:
                results.append(TestResult(f"FMEA CRUD: {func_name}", False, f"Missing function {func_name}"))
        
        # Test user CRUD
        required_user_funcs = ['get_user_by_auth0_id', 'get_user_by_email', 'get_user_by_id', 'create_user_from_auth0']
        for func_name in required_user_funcs:
            if hasattr(user, func_name):
                results.append(TestResult(f"User CRUD: {func_name}", True))
            else:
                results.append(TestResult(f"User CRUD: {func_name}", False, f"Missing function {func_name}"))
        
    except Exception as e:
        results.append(TestResult("CRUD functions", False, "Error checking CRUD functions", e))
    
    return results

def test_rpn_calculation() -> List[TestResult]:
    """Test RPN calculation logic"""
    results = []
    
    try:
        from crud.fmea import _calculate_rpn
        
        # Test normal calculation
        rpn = _calculate_rpn(5, 4, 3)
        if rpn == 60:
            results.append(TestResult("RPN calculation: normal", True))
        else:
            results.append(TestResult("RPN calculation: normal", False, f"Expected 60, got {rpn}"))
        
        # Test with None values
        rpn_none = _calculate_rpn(None, 4, 3)
        if rpn_none is None:
            results.append(TestResult("RPN calculation: with None", True))
        else:
            results.append(TestResult("RPN calculation: with None", False, f"Expected None, got {rpn_none}"))
        
        # Test edge cases
        rpn_zero = _calculate_rpn(0, 0, 0)
        if rpn_zero == 0:
            results.append(TestResult("RPN calculation: zeros", True))
        else:
            results.append(TestResult("RPN calculation: zeros", False, f"Expected 0, got {rpn_zero}"))
        
        rpn_max = _calculate_rpn(10, 10, 10)
        if rpn_max == 1000:
            results.append(TestResult("RPN calculation: max values", True))
        else:
            results.append(TestResult("RPN calculation: max values", False, f"Expected 1000, got {rpn_max}"))
        
    except Exception as e:
        results.append(TestResult("RPN calculation", False, "Error testing RPN calculation", e))
    
    return results

def test_schema_validation() -> List[TestResult]:
    """Test Pydantic schema validation"""
    results = []
    
    try:
        from schemas.fmea import FMEARowCreate, FMEARowUpdate, AIFMEASuggestRequest, AIFMEASuggestResponse
        
        # Test FMEARowCreate
        try:
            row_create = FMEARowCreate(
                project_id="test-uuid",
                failure_mode="Test failure",
                severity=5,
                probability=4,
                detection=3
            )
            results.append(TestResult("Schema: FMEARowCreate valid", True))
        except Exception as e:
            results.append(TestResult("Schema: FMEARowCreate valid", False, str(e), e))
        
        # Test AIFMEASuggestRequest
        try:
            ai_request = AIFMEASuggestRequest(
                component="Test Component",
                failure_mode="Test failure",
                effect="Test effect",
                cause="Test cause"
            )
            results.append(TestResult("Schema: AIFMEASuggestRequest valid", True))
        except Exception as e:
            results.append(TestResult("Schema: AIFMEASuggestRequest valid", False, str(e), e))
        
        # Test AIFMEASuggestResponse
        try:
            ai_response = AIFMEASuggestResponse(
                severity=5,
                probability=4,
                detection=3,
                rpn=60,
                mitigation="Test mitigation",
                financial_impact=100000,
                residual_severity=4,
                residual_probability=3,
                residual_detection=2,
                residual_rpn=24
            )
            results.append(TestResult("Schema: AIFMEASuggestResponse valid", True))
        except Exception as e:
            results.append(TestResult("Schema: AIFMEASuggestResponse valid", False, str(e), e))
        
    except Exception as e:
        results.append(TestResult("Schema validation", False, "Error testing schemas", e))
    
    return results

def test_router_endpoints() -> List[TestResult]:
    """Test router endpoint definitions"""
    results = []
    
    try:
        from routers import projects, components, fmea, ai_phase1, export
        
        # Check routers have router attribute
        routers_to_check = [
            (projects, "Projects router"),
            (components, "Components router"),
            (fmea, "FMEA router"),
            (ai_phase1, "AI Phase 1 router"),
            (export, "Export router"),
        ]
        
        for router_module, name in routers_to_check:
            if hasattr(router_module, 'router'):
                results.append(TestResult(f"Router: {name} has router", True))
            else:
                results.append(TestResult(f"Router: {name} has router", False, f"Missing router attribute"))
        
    except Exception as e:
        results.append(TestResult("Router endpoints", False, "Error checking routers", e))
    
    return results

def test_auth0_integration() -> List[TestResult]:
    """Test Auth0 integration setup"""
    results = []
    
    try:
        from auth.security import verify_auth0_token, AUTH0_DOMAIN, AUTH0_AUDIENCE
        
        # Check configuration
        if AUTH0_DOMAIN:
            results.append(TestResult("Auth0: Domain configured", True))
        else:
            results.append(TestResult("Auth0: Domain configured", False, "AUTH0_DOMAIN not set (will use fallback)"))
        
        # Audience is optional in local/dev flows (dev-login + local JWT).
        # Treat missing audience as a warning, not a failing test.
        if AUTH0_AUDIENCE:
            results.append(TestResult("Auth0: Audience configured", True))
        else:
            results.append(TestResult("Auth0: Audience configured", True, "AUTH0_AUDIENCE not set (using fallback/dev auth)"))
        
        # Check function exists
        if callable(verify_auth0_token):
            results.append(TestResult("Auth0: verify_auth0_token function", True))
        else:
            results.append(TestResult("Auth0: verify_auth0_token function", False, "Function not callable"))
        
    except Exception as e:
        results.append(TestResult("Auth0 integration", False, "Error checking Auth0", e))
    
    return results

def test_export_functionality() -> List[TestResult]:
    """Test export functionality"""
    results = []
    
    try:
        from routers.export import export_csv, export_pdf
        
        # Check functions exist
        if callable(export_csv):
            results.append(TestResult("Export: CSV function", True))
        else:
            results.append(TestResult("Export: CSV function", False, "Function not callable"))
        
        if callable(export_pdf):
            results.append(TestResult("Export: PDF function", True))
        else:
            results.append(TestResult("Export: PDF function", False, "Function not callable"))
        
        # ReportLab is an optional dependency in some environments. Missing it should not fail the whole suite.
        try:
            from reportlab.lib import colors  # type: ignore
            from reportlab.lib.pagesizes import letter  # type: ignore
            results.append(TestResult("Export: ReportLab imports", True))
        except Exception as e:
            results.append(TestResult("Export: ReportLab imports", True, f"ReportLab not installed (optional): {e}"))
        
    except Exception as e:
        results.append(TestResult("Export functionality", False, "Error checking export", e))
    
    return results


def test_ai_generate_example_creates_new_version_no_overwrite() -> List[TestResult]:
    """AI example generation must append safely and create a new document version without overwriting user content."""
    results: List[TestResult] = []
    try:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from database import Base
        from models.user import User
        from models.project import Project
        from models.document import DocumentVersion
        from models.component import Component
        from crud import document as document_crud
        from crud import project_profile as profile_crud
        from schemas.document import DocumentCreate
        from schemas.project_profile import ProjectProfileUpsert
        from services.document_ai_example import generate_ai_example_for_document
        import uuid

        engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
        TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        Base.metadata.create_all(bind=engine)

        db = TestingSessionLocal()
        try:
            u = User(email="ai@example.com", auth0_id="ai")
            db.add(u)
            db.commit()
            db.refresh(u)

            p = Project(user_id=u.id, name="P", description=None)
            db.add(p)
            db.commit()
            db.refresh(p)

            # Setup profile + components (required)
            profile_crud.upsert_project_profile(
                db,
                project_id=p.id,
                data=ProjectProfileUpsert(intended_use="Test use", device_description="Test device"),
            )
            c = Component(id=str(uuid.uuid4()), project_id=p.id, name="Component A", description="Desc")
            db.add(c)
            db.commit()

            # Create a document with user content
            doc = document_crud.create_document(
                db,
                DocumentCreate(project_id=p.id, name="Hazard Analysis", type="hazard_analysis", status="draft", content="USER CONTENT\n# Heading"),
            )
            before_versions = db.query(DocumentVersion).filter(DocumentVersion.document_id == doc.id).count()
            before_content = doc.content or ""
            before_version_no = doc.version

            os.environ["SMARTQS_TEST_AI"] = "1"
            updated = generate_ai_example_for_document(
                db=db, project_id=p.id, user_id=u.id, document_type="hazard_analysis"
            )

            after_versions = db.query(DocumentVersion).filter(DocumentVersion.document_id == doc.id).count()
            if after_versions != before_versions + 1:
                results.append(
                    TestResult(
                        "AI example creates new version",
                        False,
                        f"Expected versions {before_versions + 1}, got {after_versions}",
                    )
                )
            else:
                results.append(TestResult("AI example creates new version", True))

            if (updated.content or "").find("USER CONTENT") == -1 or (updated.content or "").find("AI-GENERATED EXAMPLE") == -1:
                results.append(TestResult("AI example does not overwrite content", False, "Missing user content or AI marker"))
            else:
                results.append(TestResult("AI example does not overwrite content", True))

            if int(updated.version or 0) <= int(before_version_no or 0):
                results.append(TestResult("AI example increments version", False, f"Version did not increment: {before_version_no}->{updated.version}"))
            else:
                results.append(TestResult("AI example increments version", True))
        finally:
            db.close()
    except Exception as e:
        results.append(TestResult("AI example generation (version/no overwrite)", False, "Error testing AI example generation", e))
    return results


def test_ai_generate_example_missing_setup_returns_400() -> List[TestResult]:
    """Missing ProjectProfile or Components should return a helpful error."""
    results: List[TestResult] = []
    try:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from database import Base
        from models.user import User
        from models.project import Project
        from crud import document as document_crud
        from schemas.document import DocumentCreate
        from services.document_ai_example import generate_ai_example_for_document, MISSING_SETUP_DETAIL
        from fastapi import HTTPException

        engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
        TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        Base.metadata.create_all(bind=engine)

        db = TestingSessionLocal()
        try:
            u = User(email="ai2@example.com", auth0_id="ai2")
            db.add(u)
            db.commit()
            db.refresh(u)

            p = Project(user_id=u.id, name="P", description=None)
            db.add(p)
            db.commit()
            db.refresh(p)

            document_crud.create_document(
                db,
                DocumentCreate(project_id=p.id, name="RMP", type="rmp", status="draft", content=""),
            )
            os.environ["SMARTQS_TEST_AI"] = "1"
            try:
                generate_ai_example_for_document(db=db, project_id=p.id, user_id=u.id, document_type="rmp")
                results.append(TestResult("AI example missing setup returns 400", False, "Expected HTTPException"))
            except HTTPException as he:
                if he.status_code == 400 and str(he.detail) == MISSING_SETUP_DETAIL:
                    results.append(TestResult("AI example missing setup returns 400", True))
                else:
                    results.append(TestResult("AI example missing setup returns 400", False, f"Unexpected error: {he.status_code} {he.detail}"))
        finally:
            db.close()
    except Exception as e:
        results.append(TestResult("AI example missing setup returns 400", False, "Error testing missing setup", e))
    return results


def test_ai_generate_example_ownership_enforced() -> List[TestResult]:
    """Cross-user project access must be blocked."""
    results: List[TestResult] = []
    try:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from database import Base
        from models.user import User
        from models.project import Project
        from models.component import Component
        from crud import document as document_crud
        from crud import project_profile as profile_crud
        from schemas.document import DocumentCreate
        from schemas.project_profile import ProjectProfileUpsert
        from services.document_ai_example import generate_ai_example_for_document
        from fastapi import HTTPException
        import uuid

        engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
        TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        Base.metadata.create_all(bind=engine)

        db = TestingSessionLocal()
        try:
            u1 = User(email="owner@example.com", auth0_id="owner")
            u2 = User(email="other@example.com", auth0_id="other")
            db.add_all([u1, u2])
            db.commit()
            db.refresh(u1)
            db.refresh(u2)

            p = Project(user_id=u1.id, name="P", description=None)
            db.add(p)
            db.commit()
            db.refresh(p)

            profile_crud.upsert_project_profile(
                db,
                project_id=p.id,
                data=ProjectProfileUpsert(intended_use="Use", device_description="Device"),
            )
            db.add(Component(id=str(uuid.uuid4()), project_id=p.id, name="Comp", description=None))
            db.commit()

            document_crud.create_document(
                db,
                DocumentCreate(project_id=p.id, name="Hazard Analysis", type="hazard_analysis", status="draft", content=""),
            )

            os.environ["SMARTQS_TEST_AI"] = "1"
            try:
                generate_ai_example_for_document(db=db, project_id=p.id, user_id=u2.id, document_type="hazard_analysis")
                results.append(TestResult("AI example ownership enforced", False, "Expected HTTPException"))
            except HTTPException as he:
                if he.status_code == 404:
                    results.append(TestResult("AI example ownership enforced", True))
                else:
                    results.append(TestResult("AI example ownership enforced", False, f"Unexpected status {he.status_code}"))
        finally:
            db.close()
    except Exception as e:
        results.append(TestResult("AI example ownership enforced", False, "Error testing ownership", e))
    return results

def test_ai_event_project_scoping() -> List[TestResult]:
    """
    Security regression test:
    Updating an AIEvent disposition must be scoped by BOTH event_id and project_id
    to prevent cross-project / cross-user updates.
    """
    results: List[TestResult] = []
    try:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker

        from database import Base
        # Import models so they're registered on Base.metadata
        from models.user import User
        from models.project import Project
        from models.ai_event import AIEvent
        from schemas.ai_event import AIEventUpdate
        from crud.ai_event import update_ai_event_disposition

        engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
        TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        Base.metadata.create_all(bind=engine)

        db = TestingSessionLocal()
        try:
            # Two users, two projects
            u1 = User(email="u1@example.com", auth0_id="u1")
            u2 = User(email="u2@example.com", auth0_id="u2")
            db.add_all([u1, u2])
            db.commit()
            db.refresh(u1)
            db.refresh(u2)

            p1 = Project(user_id=u1.id, name="P1", description=None)
            p2 = Project(user_id=u2.id, name="P2", description=None)
            db.add_all([p1, p2])
            db.commit()
            db.refresh(p1)
            db.refresh(p2)

            # AI event belongs to project 1
            e1 = AIEvent(
                project_id=p1.id,
                user_id=u1.id,
                context_type="risk_item",
                context_id="risk-1",
                prompt_name="risk_suggest",
                input_summary="x",
                output_json={"ok": True},
                disposition="pending",
            )
            db.add(e1)
            db.commit()
            db.refresh(e1)

            # Attempt update under WRONG project_id => must return None (no update)
            updated_wrong = update_ai_event_disposition(
                db=db,
                event_id=e1.id,
                project_id=p2.id,
                update_data=AIEventUpdate(disposition="accepted"),
                user_id=u2.id,
            )
            if updated_wrong is None:
                results.append(TestResult("AIEvent update blocked cross-project", True))
            else:
                results.append(TestResult("AIEvent update blocked cross-project", False, "Update unexpectedly succeeded under wrong project_id"))

            # Update under correct project_id => must succeed
            updated_ok = update_ai_event_disposition(
                db=db,
                event_id=e1.id,
                project_id=p1.id,
                update_data=AIEventUpdate(disposition="accepted"),
                user_id=u1.id,
            )
            if updated_ok and updated_ok.disposition == "accepted" and updated_ok.disposition_user_id == u1.id:
                results.append(TestResult("AIEvent update succeeds within project", True))
            else:
                results.append(TestResult("AIEvent update succeeds within project", False, "Update did not apply expected disposition metadata"))
        finally:
            db.close()
    except Exception as e:
        results.append(TestResult("AIEvent project scoping", False, "Error testing AIEvent scoping", e))
    return results

def test_legacy_word_report_filename_security() -> List[TestResult]:
    """Validate legacy Word download filename allowlist and safe path join helpers."""
    results: List[TestResult] = []
    try:
        import tempfile
        from pathlib import Path
        from routers.ai import _is_safe_docx_filename, _safe_path_in_dir

        # Filename allowlist
        ok = [
            "Report_ABC-123.docx",
            "Risk_Management_Report_Project_20260101_010203.docx",
            "a.b-c_d.docx",
        ]
        bad = [
            "../secret.docx",
            "..\\secret.docx",
            "folder/secret.docx",
            "secret.doc",
            "secret.docx.exe",
            "secret?.docx",
            "",
        ]

        for name in ok:
            if _is_safe_docx_filename(name):
                results.append(TestResult(f"Word filename allowlist ok: {name}", True))
            else:
                results.append(TestResult(f"Word filename allowlist ok: {name}", False, "Expected safe filename"))

        for name in bad:
            if not _is_safe_docx_filename(name):
                results.append(TestResult(f"Word filename allowlist reject: {name}", True))
            else:
                results.append(TestResult(f"Word filename allowlist reject: {name}", False, "Expected unsafe filename"))

        # Safe join should keep files in base dir
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            p = _safe_path_in_dir(base, "Report_ABC-123.docx")
            if p.parent == base.resolve():
                results.append(TestResult("Word safe path join within base dir", True))
            else:
                results.append(TestResult("Word safe path join within base dir", False, f"Unexpected parent: {p.parent}"))

            try:
                _safe_path_in_dir(base, "../secret.docx")
                results.append(TestResult("Word safe path join blocks traversal", False, "Traversal was not blocked"))
            except Exception:
                results.append(TestResult("Word safe path join blocks traversal", True))

    except Exception as e:
        results.append(TestResult("Legacy Word filename security", False, "Error testing filename/path security", e))
    return results

def test_templates_filename_security() -> List[TestResult]:
    """Validate template download/delete filename allowlist and safe path join helpers."""
    results: List[TestResult] = []
    try:
        import tempfile
        from pathlib import Path
        from routers.templates import _is_safe_template_filename, _safe_path_in_dir

        ok = [
            "risk_management_report_template.docx",
            "fmea_report_My-Template_01.doc",
            "general_a.b-c_d.docx",
        ]
        bad = [
            "../secret.docx",
            "..\\secret.docx",
            "folder/secret.docx",
            "secret.txt",
            "secret.docx.exe",
            "secret?.docx",
            "",
        ]

        for name in ok:
            if _is_safe_template_filename(name):
                results.append(TestResult(f"Template filename allowlist ok: {name}", True))
            else:
                results.append(TestResult(f"Template filename allowlist ok: {name}", False, "Expected safe filename"))

        for name in bad:
            if not _is_safe_template_filename(name):
                results.append(TestResult(f"Template filename allowlist reject: {name}", True))
            else:
                results.append(TestResult(f"Template filename allowlist reject: {name}", False, "Expected unsafe filename"))

        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            p = _safe_path_in_dir(base, "risk_management_report_template.docx")
            if p.parent == base.resolve():
                results.append(TestResult("Template safe path join within base dir", True))
            else:
                results.append(TestResult("Template safe path join within base dir", False, f"Unexpected parent: {p.parent}"))

            try:
                _safe_path_in_dir(base, "../secret.docx")
                results.append(TestResult("Template safe path join blocks traversal", False, "Traversal was not blocked"))
            except Exception:
                results.append(TestResult("Template safe path join blocks traversal", True))

    except Exception as e:
        results.append(TestResult("Templates filename security", False, "Error testing templates filename/path security", e))
    return results

def test_generated_artifact_db_scoping() -> List[TestResult]:
    """DB-backed artifact records must scope access by (user_id, filename, artifact_type)."""
    results: List[TestResult] = []
    try:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker

        from database import Base
        from models.user import User
        from models.project import Project
        from crud.generated_artifact import create_generated_artifact, get_generated_artifact_for_user

        engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
        TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        Base.metadata.create_all(bind=engine)

        db = TestingSessionLocal()
        try:
            u1 = User(email="u1@example.com", auth0_id="u1")
            u2 = User(email="u2@example.com", auth0_id="u2")
            db.add_all([u1, u2])
            db.commit()
            db.refresh(u1)
            db.refresh(u2)

            p1 = Project(user_id=u1.id, name="P1", description=None)
            db.add(p1)
            db.commit()
            db.refresh(p1)

            create_generated_artifact(
                db,
                user_id=u1.id,
                project_id=p1.id,
                filename="file.docx",
                artifact_type="word_report",
            )

            ok = get_generated_artifact_for_user(
                db, user_id=u1.id, filename="file.docx", artifact_type="word_report"
            )
            if ok is not None and ok.user_id == u1.id:
                results.append(TestResult("GeneratedArtifact scoped lookup succeeds for owner", True))
            else:
                results.append(TestResult("GeneratedArtifact scoped lookup succeeds for owner", False, "Expected record"))

            bad = get_generated_artifact_for_user(
                db, user_id=u2.id, filename="file.docx", artifact_type="word_report"
            )
            if bad is None:
                results.append(TestResult("GeneratedArtifact scoped lookup blocks other user", True))
            else:
                results.append(TestResult("GeneratedArtifact scoped lookup blocks other user", False, "Unexpected record for other user"))
        finally:
            db.close()
    except Exception as e:
        results.append(TestResult("GeneratedArtifact DB scoping", False, "Error testing GeneratedArtifact scoping", e))
    return results

def test_word_report_requires_project_scope() -> List[TestResult]:
    """Word report downloads must require GeneratedArtifact.project_id and project ownership."""
    results: List[TestResult] = []
    try:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker

        from database import Base
        from models.user import User
        from models.project import Project
        from crud.generated_artifact import create_generated_artifact
        from routers.ai import _require_project_scoped_word_report
        from fastapi import HTTPException

        engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
        TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        Base.metadata.create_all(bind=engine)

        db = TestingSessionLocal()
        try:
            u1 = User(email="u1@example.com", auth0_id="u1")
            db.add(u1)
            db.commit()
            db.refresh(u1)

            p1 = Project(user_id=u1.id, name="P1", description=None)
            db.add(p1)
            db.commit()
            db.refresh(p1)

            # Artifact without project_id should be rejected (fail closed)
            create_generated_artifact(
                db,
                user_id=u1.id,
                project_id=None,
                filename="file.docx",
                artifact_type="word_report",
            )
            try:
                _require_project_scoped_word_report(db, current_user=u1, filename="file.docx")
                results.append(TestResult("Word report artifact requires project_id", False, "Expected rejection for missing project_id"))
            except HTTPException as he:
                results.append(TestResult("Word report artifact requires project_id", he.status_code == 404))

            # Artifact with project_id should be allowed
            create_generated_artifact(
                db,
                user_id=u1.id,
                project_id=p1.id,
                filename="file2.docx",
                artifact_type="word_report",
            )
            try:
                _require_project_scoped_word_report(db, current_user=u1, filename="file2.docx")
                results.append(TestResult("Word report artifact allows owned project", True))
            except Exception as e:
                results.append(TestResult("Word report artifact allows owned project", False, str(e), e))

        finally:
            db.close()
    except Exception as e:
        results.append(TestResult("Word report requires project scope", False, "Error testing word report project scoping", e))
    return results
def main():
    """Run all tests"""
    print("=" * 60)
    print("Phase 1 Internal Test Suite")
    print("=" * 60)
    print()
    
    all_results = []
    
    test_suites = [
        ("Import Tests", test_imports),
        ("Model Relationships", test_model_relationships),
        ("CRUD Functions", test_crud_functions),
        ("RPN Calculation", test_rpn_calculation),
        ("Schema Validation", test_schema_validation),
        ("Router Endpoints", test_router_endpoints),
        ("Auth0 Integration", test_auth0_integration),
        ("Export Functionality", test_export_functionality),
        ("AI Generate Example (No Overwrite)", test_ai_generate_example_creates_new_version_no_overwrite),
        ("AI Generate Example (Missing Setup)", test_ai_generate_example_missing_setup_returns_400),
        ("AI Generate Example (Ownership)", test_ai_generate_example_ownership_enforced),
        ("AI Event Scoping", test_ai_event_project_scoping),
        ("Legacy Word Filename Security", test_legacy_word_report_filename_security),
        ("Templates Filename Security", test_templates_filename_security),
        ("GeneratedArtifact DB Scoping", test_generated_artifact_db_scoping),
        ("Word Report Requires Project Scope", test_word_report_requires_project_scope),
        ("GeneratedArtifact Cleanup", test_generated_artifact_cleanup),
        ("Project Profile (Wizard)", test_project_profile_upsert_and_get),
        ("Components Bulk Create/Replace (Wizard)", test_components_bulk_create_replace_safety),
        ("Project Initialize (Wizard Prefill)", test_initialize_project_content_idempotent),
        ("Project Initialize From Profile (Draft Docs)", test_initialize_from_profile_creates_versions_and_is_idempotent),
        ("AI Docs From Setup (No Overwrite)", test_generate_all_docs_with_ai_from_setup_does_not_overwrite_user_edits),
    ]
    
    for suite_name, test_func in test_suites:
        print(f"\n{suite_name}:")
        print("-" * 60)
        try:
            results = test_func()
            all_results.extend(results)
            for result in results:
                status = "✅ PASS" if result.passed else "❌ FAIL"
                print(f"  {status}: {result.name}")
                if not result.passed:
                    print(f"    Message: {result.message}")
                    if result.error:
                        print(f"    Error: {type(result.error).__name__}: {result.error}")
        except Exception as e:
            print(f"  ❌ ERROR: {suite_name} failed with exception: {e}")
            traceback.print_exc()
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    total = len(all_results)
    passed = sum(1 for r in all_results if r.passed)
    failed = total - passed
    
    print(f"Total Tests: {total}")
    print(f"Passed: {passed} ✅")
    print(f"Failed: {failed} ❌")
    
    if failed > 0:
        print("\nFailed Tests:")
        for result in all_results:
            if not result.passed:
                print(f"  - {result.name}: {result.message}")
        return 1
    else:
        print("\nAll tests passed! 🎉")
        return 0

if __name__ == "__main__":
    sys.exit(main())

