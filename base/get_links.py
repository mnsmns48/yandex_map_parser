import os
import random
import time
import asyncio
import undetected_chromedriver as uc

from pathlib import Path
from bs4 import BeautifulSoup
from selenium.common import MoveTargetOutOfBoundsException, NoSuchElementException, StaleElementReferenceException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from base.bs_processing import pars_inner_info
from base.config import hidden
from base.crud import write_links
from base.engine import db
from base.models import Base

path = Path(os.path.abspath(__file__)).parent.parent


async def get_links_data(region: str, category: str, count: int):
    driver = uc.Chrome(headless=False,
                       use_subprocess=False,
                       version_main=114,
                       driver_executable_path=f'{path}/chromedriver')
    driver.maximize_window()
    driver.get('https://www.google.ru')
    await asyncio.sleep(random.uniform(0.4, 1))
    driver.find_element(By.XPATH, '//textarea[@aria-label]').send_keys('Yandex maps')
    await asyncio.sleep(random.uniform(0.4, 1))
    driver.find_element(By.XPATH, '//input[@aria-label]').click()
    await asyncio.sleep(random.uniform(0.4, 1))
    driver.find_element(By.XPATH, '//h3[1]').click()
    await asyncio.sleep(random.randint(1, 3))
    driver.switch_to.window(driver.window_handles[1])
    driver.find_element(by=By.CSS_SELECTOR,
                        value='[placeholder="Поиск мест и адресов"]').send_keys(f"{region} {category}")
    time.sleep(random.uniform(0.4, 0.8))
    driver.find_element(By.CSS_SELECTOR, '[class="small-search-form-view__button"]').click()
    await asyncio.sleep(random.randint(1, 3))
    slider = driver.find_element(By.CSS_SELECTOR, '[class="scroll__scrollbar-thumb"]')
    slide_offset = 1
    errors = 0
    driver.implicitly_wait(2)
    while True:
        try:
            action = ActionChains(driver)
            if slide_offset == 10:
                errors += 1
                print('errors:', errors)
                slide_offset = 1
            y_point = int(100 / (errors + 1) / slide_offset)
            action.click_and_hold(slider)
            action.move_by_offset(0, y_point)
            action.release()
            action.perform()
            hrefs = driver.find_elements(By.CSS_SELECTOR, "[class='search-business-snippet-view__content']")
            end = driver.find_elements(By.CSS_SELECTOR, '[class="add-business-view"]')
            print(f'Offset: {slide_offset} Urls: {len(hrefs)}')
            if len(end) > 0 or len(hrefs) > count:
                print('\n---exit from cycle---\n')
                line_n = 1
                for line in hrefs:
                    line.click()
                    print(line_n)
                    await asyncio.sleep(random.uniform(2.5, 3.5))
                    card = driver.find_element(By.XPATH, "//div[@class='business-card-view']")
                    soup = BeautifulSoup(markup=card.get_attribute('innerHTML'), features='lxml')
                    try:
                        data = await pars_inner_info(soup=soup,
                                                     requested_region=region,
                                                     city_status=hidden.city)
                        async with db.scoped_session() as session:
                            await write_links(session=session,
                                              table=Base.metadata.tables.get(hidden.db_table_name),
                                              data=data)
                    except (ValueError, StaleElementReferenceException):
                        continue
                    line_n += 1
                break
        except MoveTargetOutOfBoundsException:
            slide_offset += 1
        except NoSuchElementException:
            await asyncio.sleep(30)
            driver.refresh()
            await asyncio.sleep(3)
    print('Finish this request')
    driver.close()


async def link_collection_processing(regions: list, category: str, count: int):
    for reg in regions:
        start_time = time.time()
        await get_links_data(region=reg, category=category, count=count)
        print(f'Location: <{reg}> Time: {time.time() - start_time}')
