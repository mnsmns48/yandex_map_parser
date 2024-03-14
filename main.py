import asyncio

from asyncpg import InvalidCatalogNameError
from base.engine import db, create_db
from base.get_links import link_collection_processing
from base.models import Base


async def main():
    try:
        async with db.engine.begin() as async_connect:
            await async_connect.run_sync(Base.metadata.create_all)
    except InvalidCatalogNameError:
        await asyncio.create_task(create_db())
        async with db.engine.begin() as async_connect:
            await async_connect.run_sync(Base.metadata.create_all)
    await link_collection_processing(regions=['Москва'],
                                     category='Стоматология',
                                     count=950)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Script stopped')