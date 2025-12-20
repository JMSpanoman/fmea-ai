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
        ("models.fmea", "FMEARow model"),
        ("models.fmea_version", "FMEAVersion model"),
        ("models.risk_item", "RiskItem model"),
        ("crud.user", "User CRUD"),
        ("crud.project", "Project CRUD"),
        ("crud.component", "Component CRUD"),
        ("crud.fmea", "FMEA CRUD"),
        ("crud.risk_item", "Risk Item CRUD"),
        ("schemas.project", "Project schemas"),
        ("schemas.component", "Component schemas"),
        ("schemas.fmea", "FMEA schemas"),
        ("schemas.risk_item", "Risk Item schemas"),
        ("auth.security", "Auth security"),
        ("auth.dependencies", "Auth dependencies"),
        ("routers.projects", "Projects router"),
        ("routers.components", "Components router"),
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
        else:
            results.append(TestResult("FMEAVersion.fmea_row relationship", False, "Missing fmea_row relationship"))
        
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
        
        if AUTH0_AUDIENCE:
            results.append(TestResult("Auth0: Audience configured", True))
        else:
            results.append(TestResult("Auth0: Audience configured", False, "AUTH0_AUDIENCE not set (will use fallback)"))
        
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
        
        # Check reportlab import
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import letter
            results.append(TestResult("Export: ReportLab imports", True))
        except ImportError as e:
            results.append(TestResult("Export: ReportLab imports", False, f"ReportLab not installed: {e}", e))
        
    except Exception as e:
        results.append(TestResult("Export functionality", False, "Error checking export", e))
    
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

