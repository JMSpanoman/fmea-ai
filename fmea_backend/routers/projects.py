from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def get_projects():
    return [{"id": 1, "name": "Demo Project"}]
