from fastapi import APIRouter
from starlette.responses import RedirectResponse


router = APIRouter()

@router.get("/", name="Documentation", description="API Documentation Page.")
async def main():
    """API Documentation Page."""
    return RedirectResponse(url="/docs/")