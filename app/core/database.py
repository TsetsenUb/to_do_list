from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from .config import DATABASE_URL


async_engine = create_async_engine(DATABASE_URL, echo=True)

async_session_maker = async_sessionmaker(
    bind=async_engine,
    expire_on_commit=False,
    class_=AsyncSession
)


class Base(DeclarativeBase):
    pass
