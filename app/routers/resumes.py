from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.services.resume_services import upload_resume, get_resume
from app.dependencies import get_db

router = APIRouter(prefix="/resumes", tags=["resumes"])


@router.post("/")
async def upload_user_resume(db: AsyncSession = Depends(get_db)):
    """Upload a resume."""
    return await upload_resume(db)


@router.get("/")
async def get_user_resume(db: AsyncSession = Depends(get_db)):
    """Get a resume."""
    return await get_resume(db)
