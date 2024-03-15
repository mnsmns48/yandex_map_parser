import json
from datetime import datetime

import pandas as pd
from sqlalchemy import Table, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from base.config import hidden
from base.engine import db
from base.models import ScrapeData


async def write_links(session: AsyncSession, table: Table, data: list | dict):
    stmt = insert(table).values(data).on_conflict_do_nothing()
    await session.execute(stmt)
    await session.commit()


def pandas_query(session):
    conn = session.connection()
    query = select(ScrapeData).order_by(ScrapeData.region.desc(), ScrapeData.city)
    return pd.read_sql_query(query, conn)


def time_form() -> str:
    t = datetime.now()
    return f"{t.date()}_{t.hour}-{t.minute}"


async def output_results():
    async with db.scoped_session() as session:
        df = await session.run_sync(pandas_query)
    formatted_showcase = list()
    for line in [i for i in df['showcase']]:
        formatted_showcase.append(
            [f"{i.get('service')}={i.get('price')}" for i in json.loads(line)]
        ) if line is not None else formatted_showcase.append(line)
    df['showcase'] = formatted_showcase
    filename = f'{time_form()}_{hidden.db_table_name}.xlsx'
    writer = pd.ExcelWriter(filename)
    try:
        df.to_excel(writer, index=False)
    finally:
        writer.close()
        print(f'Recorded: {filename}')
