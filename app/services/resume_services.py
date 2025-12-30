from sqlmodel.ext.asyncio.session import AsyncSession


async def upload_resume(db: AsyncSession):
    # TODO: implement

    # Example usage of db connection injection usage
    # resume = Resume(
    #     id=resume_id,
    #     user_id=user_id,
    #     file_url=file_url,
    #     status=ResumeStatus.PENDING,
    #     created_at=datetime.utcnow()
    # )

    # db.add(resume)
    # await db.commit()
    # await db.refresh(resume)
    return {"message": "Resume uploaded successfully (placeholder)"}


async def get_resume(db: AsyncSession):
    # TODO: implement
    return {"message": "Resume retrieved successfully (placeholder)"}
