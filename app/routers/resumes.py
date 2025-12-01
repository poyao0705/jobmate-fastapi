from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
# from app.services.resume_service import upload_resume, get_resume
# from app.dependencies import get_db
router = APIRouter(prefix="/resumes", tags=["resumes"])

# TODO: sample usage
# @router.post("/")
# def upload_user_resume(db: Session = Depends(get_db)):
#     """Upload a resume."""
#     return upload_resume(db)

# @router.get("/")
# def get_user_resume(db: Session = Depends(get_db)):
#     """Get a resume."""
#     return get_resume(db)
