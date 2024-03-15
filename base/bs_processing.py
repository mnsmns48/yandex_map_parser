import json
import re

from bs4 import BeautifulSoup


async def create_showcase(soup: BeautifulSoup) -> json:
    result = list()
    related_items = soup.find_all(name='div', attrs={'class': 'related-item-list-view__title'})
    related_it_prices = soup.find_all(name='div', attrs={'class': 'related-item-list-view__price'})
    if len(related_items) == len(related_it_prices) and len(related_items) > 0:
        for item, price in zip(related_items, related_it_prices):
            result.append(
                {
                    'service': item.getText(),
                    'price': price.getText()
                }
            )
    related_items_alt = soup.find_all(name='div', attrs={'class': 'related-item-photo-view__title'})
    related_it_prices_alt = soup.find_all(name='span', attrs={'class': 'related-product-view__price'})
    if len(related_items_alt) > 0:
        for item, price in zip(related_items_alt, related_it_prices_alt):
            result.append(
                {
                    'service': item.getText(),
                    'price': price.getText()
                }
            )
    if len(result) > 0:
        data = json.dumps(result)
        return data
    return None


async def create_business_contacts(soup: BeautifulSoup) -> dict:
    b_contacts = soup.find_all(name='div', attrs={'class': 'business-contacts-view__social-button'})
    result = dict()
    for line in b_contacts:
        if len(b_contacts) > 0:
            for cont in line:
                contact_ = cont.get('aria-label').split(', ')[1]
                result.update(
                    {
                        contact_: cont.get('href')
                    }
                )
    return result


def only_num(s: str) -> int:
    return int(re.sub(r'\D', '', s))


async def pars_inner_info(soup: BeautifulSoup, requested_region: str, city_status: bool) -> dict:
    category = soup.find(name='a', attrs={'class': 'business-categories-view__category'})
    name = soup.find(name='a', attrs={'class': 'card-title-view__title-link'})
    address = soup.find(name='div', attrs={'class': 'business-contacts-view__address-link'})
    phone = soup.find(name='span', attrs={'itemprop': 'telephone'})
    rank = soup.find(name='span', attrs={'class': 'business-rating-badge-view__rating-text'})
    rank_grade = soup.find(name='div', attrs={'class': 'business-header-rating-view__text _clickable'})
    link = soup.find(name='a', attrs={'class': 'card-title-view__title-link'})
    site = soup.find(name='span', attrs={'class': 'business-urls-view__text'})
    result_dict = {
        'category': category.getText() if category else None,
        'region': requested_region,
        'name': name.getText() if name else None,
        'address': address.get('aria-label') if address else None,
        'phone': phone.getText() if phone else None,
        'rank': float(rank.getText().replace(',', '.')) if rank else None,
        'rank_grade': only_num(rank_grade.getText()) if rank_grade else None,
        'link': 'https://yandex.ru' + link.get('href') if link else None,
        'site': site.getText() if site else None
    }
    if city_status:
        result_dict.update({
            'city': requested_region
        })
    else:
        result_dict.update({
            'city': address.get('aria-label').rsplit(', ', 1)[1] if address else None,
        })
    business_contacts = await create_business_contacts(soup)
    showcase = await create_showcase(soup)
    result_dict.update(business_contacts)
    if showcase:
        result_dict.update({
            'showcase': showcase
        })
    return result_dict
