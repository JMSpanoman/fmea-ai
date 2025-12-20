# Folder Structure - Phase 1

## Current Structure (Working)
```
fmea_backend/
  ├── models/          # Database models
  ├── routers/         # API endpoints
  ├── crud/            # Business logic / services
  ├── schemas/         # Pydantic schemas
  ├── auth/            # Authentication
  ├── database.py      # Database configuration
  └── main.py          # FastAPI app

frontend/src/
  ├── pages/           # Page components
  ├── components/       # Reusable components
  ├── hooks/           # React hooks
  ├── services/        # API services
  └── utils/           # Utility functions
```

## Recommended Structure (Per Specification)
```
backend/
  ├── api/             # API endpoints (routers)
  ├── models/          # Database models
  ├── db/              # Database configuration
  ├── services/        # Business logic (crud)
  └── ai/              # AI-related code

frontend/src/
  ├── pages/           # Page components
  ├── components/      # Reusable components
  ├── hooks/           # React hooks
  ├── lib/             # Libraries and utilities
  └── services/        # API services

ai_prompts/            # AI prompt templates
```

## Migration Plan

### Option 1: Gradual Migration (Recommended)
- Keep current structure working
- Create new structure alongside
- Migrate components gradually
- Update imports as needed

### Option 2: Full Reorganization
- Move files to match spec exactly
- Update all imports
- Test thoroughly
- Risk: Breaking changes

## Current Mapping

| Spec Location | Current Location | Status |
|--------------|------------------|--------|
| backend/api | fmea_backend/routers | ✅ Working |
| backend/models | fmea_backend/models | ✅ Working |
| backend/db | fmea_backend/database.py | ✅ Working |
| backend/services | fmea_backend/crud | ✅ Working |
| backend/ai | fmea_backend/routers/ai_phase1.py | ✅ Working |
| frontend/src/pages | frontend/src/pages | ✅ Working |
| frontend/src/components | frontend/src/components | ✅ Working |
| frontend/src/hooks | frontend/src/hooks | ✅ Working |
| frontend/src/lib | frontend/src/utils | ⚠️ Needs rename |
| frontend/src/services | frontend/src/services | ✅ Working |
| ai_prompts | ai_prompts/ | ✅ Created |

## Notes
- Current structure is functional and follows Python/FastAPI conventions
- Spec structure is more generic/organizational
- Can maintain both structures with symbolic links if needed
- Frontend structure already matches spec closely (just utils → lib rename)

