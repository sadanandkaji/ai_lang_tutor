from models.schema import Mistake
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

async def add_mistake(db: AsyncSession, user_id: str, mistake: str, correction: str):
    new_mistake = Mistake(user_id=user_id, mistake=mistake, correction=correction)
    db.add(new_mistake)
    await db.commit()
    await db.refresh(new_mistake)
    return new_mistake

async def get_mistakes_by_user(db: AsyncSession, user_id: str):
    result = await db.execute(select(Mistake).where(Mistake.user_id == user_id))
    return result.scalars().all()

async def delete_mistake(db: AsyncSession, mistake_id: int):
    result = await db.execute(select(Mistake).where(Mistake.id == mistake_id))
    mistake = result.scalar_one_or_none()
    if mistake:
        await db.delete(mistake)
        await db.commit()
    return mistake
