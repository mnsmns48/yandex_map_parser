import json
import random

import pandas as pd
from sqlalchemy import Table, select, Result
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from base.engine import db
from base.models import ScrapeData


async def write_links(session: AsyncSession, table: Table, data: list | dict):
    stmt = insert(table).values(data).on_conflict_do_nothing()
    await session.execute(stmt)
    await session.commit()


def pandas_query(session):
    conn = session.connection()
    query = select(ScrapeData).order_by(ScrapeData.region, ScrapeData.city)
    return pd.read_sql_query(query, conn)


async def output_results():
    async with db.scoped_session() as session:
        df = await session.run_sync(pandas_query)
    formatted_showcase = list()
    for line in [i for i in df['showcase']]:
        formatted_showcase.append(
            [f"{i.get('service')}={i.get('price')}" for i in json.loads(line)]
        ) if line is not None else formatted_showcase.append(line)
    df['showcase'] = formatted_showcase
    filename = f'output{random.randint(0, 100)}.xlsx'
    writer = pd.ExcelWriter(filename)
    try:
        df.to_excel(writer, index=False)
    finally:
        writer.close()
        print(f'записана в файл: {filename}')

    #
    # query = select(ScrapeData).order_by(ScrapeData.region, ScrapeData.id).limit(20)
    # async with db.engine.begin() as conn:
    # r: Result = await session.execute(query)
    # result = r.scalars().all()
    #     df = await pd.read_sql(sql=query, con=conn)
    # print(df)
    # df = pd.DataFrame(columns=[i for i in ScrapeData.__annotations__.keys()])
    # for line in result:
    #     if line.showcase:
    #         data = {'showcase': json.loads(line.showcase)}
    #         df._append(data, ignore_index=True)
    # print(df)
    # filename = f'output{random.randint(0, 100)}.xlsx'
    # writer = pd.ExcelWriter(filename)
    # try:
    #     df.to_excel(writer, index=False)
    # finally:
    #     writer.close()
    #     print(f'записана в файл: {filename}')
