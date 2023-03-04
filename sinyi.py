import re
from multiprocessing import Pool, cpu_count
from urllib.parse import urljoin

import pandas as pd
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

# 偽裝成瀏覽器發送請求
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/58.0.3029.110 Safari/537.3 '
}
base_url = 'https://www.sinyi.com.tw'


def num_extract(string):
    match = re.search(r'\d+\.\d+', string)
    return match.group() if match else None


def page_proces(target_url):
    house_list = []
    res = requests.get(target_url, headers=headers)
    soup = BeautifulSoup(res.text, 'lxml')
    list_items = soup.find("div", class_="buy-list-frame")
    list_items = list_items.find_all("div", class_="buy-list-item")

    for li in list_items:
        price = li.find("div", class_="LongInfoCard_Type_Right")
        address_info = li.find("div", class_="LongInfoCard_Type_Address").find_all('span')
        house_info = li.find("div", class_="LongInfoCard_Type_HouseInfo").find_all('span')
        item = {
            'title': li.find("div", class_="LongInfoCard_Type_Name").text,
            'price': price.select('span[style*="color:#dd2525"]')[0].text,
            'price_sub': None if price.find('span', text='(含車位價)') is None else '(含車位價)',
            'address': address_info[0].text,
            'type': address_info[2].text,
            'age': float(address_info[1].text.replace('年', '')) if address_info[1].text.replace('年', '') not in [
                '--', '預售'] else None,
            'floor': house_info[-1].text,
            '地': float(li.select_one('span:contains("地坪")').text.split(' ')[-1]) if li.select_one(
                'span:contains("地坪")') is not None else None,
            '實': num_extract(li.select_one('span:contains("主")').text) if li.select_one('span:contains("主")') else None,
            '建': float(li.select_one('span:contains("建坪")').text.split(' ')[-1]) if li.select_one(
                'span:contains("建坪")') is not None else None,
            '格局': house_info[2].text,
            'url': urljoin(base_url, li.find("a")['href'])
        }
        house_list.append(item)
    return house_list


if __name__ == '__main__':
    budget = '1500'
    budget_end = '2500'
    if len(budget) > 1:
        budget = f'/{budget}-{budget_end}-price'
    elif len(budget_end) > 1:
        budget = f'/{budget_end}-down-price'

    year = '10'
    year_end = '30'
    if len(year) > 1:
        year = f'/{year}-{year_end}-year'
    elif len(year_end) > 1:
        year = f'/{year_end}-down-year'

    url = f'/buy/list{budget}/apartment-dalou-huaxia-flat-townhouse-villa-type{year}/Taipei-city/Taipei-R-mrtline/03-mrt/price-asc/index'
    url = urljoin(base_url, url)

    max_page = requests.get(url, headers=headers)
    max_page = BeautifulSoup(max_page.text, 'lxml')

    max_page = int(max_page.find_all("li", class_="pageClassName")[-1].text)
    urls = [url.replace('index', str(i + 1)) for i in range(max_page)]

    p = Pool(int(cpu_count() * 0.8))
    result = list(tqdm(p.imap(page_proces, urls), total=len(urls)))
    p.close()
    p.join()

    result = [item for sublist in result for item in sublist]

    df = pd.DataFrame(result)
