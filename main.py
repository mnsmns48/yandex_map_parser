import asyncio

from asyncpg import InvalidCatalogNameError

from base.crud import output_results
from base.engine import db, create_db
from base.get_links import link_collection_processing
from base.models import Base
from base.config import hidden


async def main():
    try:
        async with db.engine.begin() as async_connect:
            await async_connect.run_sync(Base.metadata.create_all)
    except InvalidCatalogNameError:
        await asyncio.create_task(create_db())
        async with db.engine.begin() as async_connect:
            await async_connect.run_sync(Base.metadata.create_all)
    print('Press 1 to parsing\n'
          'Press 2 to output_result')
    try:
        choice = int(input())

        if choice == 1:
            await link_collection_processing(regions=hidden.region,
                                             category=hidden.category,
                                             count=hidden.max_page_count)
        elif choice == 2:
            await output_results()
        else:
            print('Unknown choice')
    except TypeError:
        print('It is necessary to make a choice by number')


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Script stopped')
