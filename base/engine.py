import asyncpg
from asyncio import current_task
from contextlib import asynccontextmanager
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import async_scoped_session, AsyncSession, async_sessionmaker, create_async_engine

from base.config import hidden


class Settings():
    def __init__(self, db):
        self.db = db
        self.db_url: str = (f"postgresql+asyncpg://{hidden.db_username}:{hidden.db_password}"
                            f"@localhost:{hidden.db_local_port}/{self.db}")
        self.db_echo: bool = False


main_settings = Settings(db=hidden.db_name)


class DataBase:
    def __init__(self, url: str, echo: bool = False):
        self.engine = create_async_engine(
            url=url,
            echo=echo,
            poolclass=NullPool
        )
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )

    @asynccontextmanager
    async def scoped_session(self) -> AsyncSession:
        session = async_scoped_session(
            session_factory=self.session_factory,
            scopefunc=current_task,
        )
        try:
            async with session() as s:
                yield s
        finally:
            await session.remove()


db = DataBase(main_settings.db_url, main_settings.db_echo)


async def create_db():
    conn = await asyncpg.connect(database='postgres',
                                 user=hidden.db_username,
                                 password=hidden.db_password,
                                 host='localhost',
                                 port=hidden.db_local_port
                                 )
    sql = f'CREATE DATABASE "{hidden.db_name}"'
    await conn.execute(sql)
    await conn.close()
    print(f"DB <{hidden.db_name}> success created")
