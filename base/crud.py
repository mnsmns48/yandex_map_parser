from sqlalchemy import Table
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession


async def write_links(session: AsyncSession, table: Table, data: list | dict):
    stmt = insert(table).values(data).on_conflict_do_nothing()
    await session.execute(stmt)
    await session.commit()
