import aiohttp
from bs4 import BeautifulSoup
from sqlalchemy import Table
from sqlalchemy.dialects.postgresql import insert

from sqlalchemy.ext.asyncio import AsyncSession

from base.config import ua
from base.engine import db
from base.models import Rubrikator


async def write_data(session: AsyncSession, table: Table, values: list | dict):
    stmt = insert(table).values(values)
    await session.execute(stmt)
    await session.commit()


async def get_page():
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        async with session.get(url='https://yandex.ru/support/nmaps/app_poi.html',
                               headers={
                                   'user-agent': ua.random
                               }
                               ) as response:
            html_code = await response.text()
    return html_code


async def bs_work(page: str):
    values = list()
    soup = BeautifulSoup(markup=page, features='lxml')
    # menu1 = soup.find_all(name='a', attrs={'class': 'xref doc-c-link'})
    menu1 = soup.find_all(name='dt', attrs={'class': 'dt dlterm doc-c-list doc-c-list__dt'})
    for line in menu1:
        value = line.getText().split('. ', 1)
        try:
            values.append(
                {
                    'id': value[0],
                    'title': value[1]
                }
            )
        except IndexError:
            pass
    async with db.scoped_session() as session:
        await write_data(session=session,
                         table=Rubrikator.metadata.tables.get('rubrikator'),
                         values=values)


async def rubrikator():
    result = await get_page()
    await bs_work(result)
