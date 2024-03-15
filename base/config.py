from dataclasses import dataclass
from environs import Env
from fake_useragent import UserAgent


@dataclass
class Hidden:
    db_username: str
    db_password: str
    db_local_port: int
    db_name: str
    db_table_name: str
    region: list[str]
    city: bool
    category: str
    max_page_count: int


def load_hidden_vars(path: str):
    env = Env()
    env.read_env()

    return Hidden(
        db_username=env.str("DB_USERNAME"),
        db_password=env.str("DB_PASSWORD"),
        db_local_port=env.int("DB_LOCAL_PORT"),
        db_name=env.str("DB_NAME"),
        db_table_name=env.str("TABLENAME"),
        region=list(map(str, env.list("REGION"))),
        city=env.bool("CITY"),
        category=env.str("CATEGORY"),
        max_page_count=env.int("MAX_PAGE_COUNT")
    )


hidden = load_hidden_vars(path='../.env')
ua = UserAgent()
