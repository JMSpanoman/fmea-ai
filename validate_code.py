#!/usr/bin/env python3
"""
Static Code Validation Script
Checks for common issues without requiring dependencies
"""

import os
import re
from pathlib import Path

def check_file_exists(filepath: str) -> tuple[bool, str]:
    """Check if file exists"""
    if os.path.exists(filepath):
        return True, f"✅ {filepath} exists"
    return False, f"❌ {filepath} missing"

def check_imports(filepath: str) -> list[tuple[bool, str]]:
    """Check for common import issues"""
    results = []
    try:
        with open(filepath, 'r') as f:
            content = f.read()
            
        # Check for old FMEA import
        if 'from models.fmea import FMEA' in content and 'FMEARow' not in content:
            results.append((False, f"❌ {filepath}: Uses old FMEA import, should use FMEARow"))
        
        # Check for .dict() usage (Pydantic v1)
        if '.dict(' in content and 'model_dump' not in content:
            # Check if it's in a compatibility block
            if 'hasattr' not in content or 'model_dump' not in content:
                results.append((True, f"⚠️  {filepath}: Uses .dict() - ensure Pydantic v2 compatibility"))
        
        # Check for missing error handling in critical functions
        if 'def create_' in content or 'def update_' in content:
            if 'try:' not in content and 'except' not in content:
                results.append((True, f"⚠️  {filepath}: Consider adding error handling"))
        
    except Exception as e:
        results.append((False, f"❌ Error reading {filepath}: {e}"))
    
    return results

def check_router_paths(filepath: str) -> list[tuple[bool, str]]:
    """Check router path consistency"""
    results = []
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Check for router prefix and endpoint path conflicts
        prefix_match = re.search(r'APIRouter\(prefix=["\']([^"\']+)["\']', content)
        if prefix_match:
            prefix = prefix_match.group(1)
            # Check if endpoints use the prefix redundantly
            if prefix and f'@router.get("{prefix}' in content:
                results.append((False, f"❌ {filepath}: Endpoint path may conflict with router prefix"))
    except Exception as e:
        results.append((False, f"❌ Error checking {filepath}: {e}"))
    
    return results

def main():
    """Run validation checks"""
    print("=" * 60)
    print("Phase 1 Code Validation")
    print("=" * 60)
    print()
    
    backend_path = Path("fmea_backend")
    frontend_path = Path("frontend/src")
    
    all_results = []
    
    # Check critical files exist
    print("File Existence Checks:")
    print("-" * 60)
    critical_files = [
        "fmea_backend/models/user.py",
        "fmea_backend/models/project.py",
        "fmea_backend/models/component.py",
        "fmea_backend/models/fmea.py",
        "fmea_backend/models/fmea_version.py",
        "fmea_backend/routers/projects.py",
        "fmea_backend/routers/components.py",
        "fmea_backend/routers/fmea.py",
        "fmea_backend/routers/ai_phase1.py",
        "fmea_backend/routers/export.py",
        "frontend/src/types.ts",
        "frontend/src/services/apiPhase1.ts",
        "frontend/src/components/FMEA/AiSidebar.tsx",
        "frontend/src/components/FMEA/DiffViewer.tsx",
        "frontend/src/components/FMEA/FinancialRiskPanel.tsx",
        "frontend/src/components/FMEA/ExportControls.tsx",
    ]
    
    for filepath in critical_files:
        exists, msg = check_file_exists(filepath)
        print(f"  {msg}")
        all_results.append((exists, msg))
    
    # Check imports
    print("\nImport Checks:")
    print("-" * 60)
    files_to_check = [
        "fmea_backend/main.py",
        "fmea_backend/routers/fmea.py",
        "fmea_backend/crud/fmea.py",
        "fmea_backend/crud/project.py",
        "fmea_backend/crud/component.py",
    ]
    
    for filepath in files_to_check:
        if os.path.exists(filepath):
            results = check_imports(filepath)
            for result in results:
                print(f"  {result[1]}")
                all_results.append(result)
    
    # Check router paths
    print("\nRouter Path Checks:")
    print("-" * 60)
    router_files = [
        "fmea_backend/routers/projects.py",
        "fmea_backend/routers/components.py",
        "fmea_backend/routers/fmea.py",
    ]
    
    for filepath in router_files:
        if os.path.exists(filepath):
            results = check_router_paths(filepath)
            for result in results:
                print(f"  {result[1]}")
                all_results.append(result)
    
    # Summary
    print("\n" + "=" * 60)
    print("Validation Summary")
    print("=" * 60)
    
    total = len(all_results)
    passed = sum(1 for r in all_results if r[0])
    failed = total - passed
    
    print(f"Total Checks: {total}")
    print(f"Passed: {passed} ✅")
    print(f"Failed/Warnings: {failed} ⚠️")
    
    if failed > 0:
        print("\nIssues Found:")
        for result in all_results:
            if not result[0] or '⚠️' in result[1]:
                print(f"  {result[1]}")
        return 1
    else:
        print("\nAll checks passed! 🎉")
        return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())

