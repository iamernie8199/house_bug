import re
from multiprocessing import Pool, cpu_count
from urllib.parse import urljoin

import pandas as pd
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/58.0.3029.110 Safari/537.3 '
}
yungching_url = 'https://buy.yungching.com.tw'


def num_extract(string):
    match = re.search(r'\d+\.\d+', string)
    return match.group() if match else None


def page_process(target_url):
    house_list = []
    res = requests.get(target_url, headers=headers)
    soup = BeautifulSoup(res.text, 'lxml')
    list_items = soup.find_all("li", class_="m-list-item")
    for li in list_items:
        info = li.find("ul", class_="item-info-detail")
        item = {
            'title': li.find("h3").text,
            'price': float(li.find("span", class_="price-num").text.replace(',', '')),
            'price_sub': li.find("div", class_="sub-price").text,
            'address': li.find("span").text,
            'type': info.find_all("li")[0].text,
            'age': re.search(r'\d+\.\d+', info.find_all("li")[1].text).group(),
            'floor': info.find_all("li")[2].text.replace('\r\n', '').strip(),
            '地': num_extract(info.find_all("li")[3].text),
            '實': num_extract(info.find_all("li")[4].text),
            '建': num_extract(info.find_all("li")[5].text),
            '格局': info.find_all("li")[6].text.replace('\r\n', '').strip(),
            'url': urljoin(yungching_url, li.find("a")['href'])
        }
        house_list.append(item)
    return house_list


if __name__ == '__main__':
    region = '台北市'
    region_sub = ''
    budget_start = '1500'
    budget_end = '2500'
    age_start = ''
    age_end = '30'
    url = f'{yungching_url}/region/{region}-{region_sub}_c/{budget_start}-{budget_end}_price/{age_start}-{age_end}_age/'

    max_page = requests.get(url, headers=headers)
    max_page = BeautifulSoup(max_page.text, 'lxml')

    url = max_page.find('a', text='最末頁')['href']
    max_page = int(url.split('=')[-1])
    url = urljoin(yungching_url, url)
    url = url.split('=')[0] + '='
    urls = [url + str(i + 1) for i in range(max_page)]

    p = Pool(int(cpu_count() * 0.8))
    result = list(tqdm(p.imap(page_process, urls), total=len(urls)))
    p.close()
    p.join()

    result = [item for sublist in result for item in sublist]

    df = pd.DataFrame(result)
    df.to_csv('out.csv', encoding="utf_8_sig")