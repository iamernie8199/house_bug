import pandas as pd
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from multiprocessing import Pool, cpu_count


def page_proces(target_url):
    house_list = []
    driver_c = webdriver.Chrome(ChromeDriverManager().install())
    driver_c.get(target_url)

    list_items = driver_c.find_elements('class name', 'm-list-item')
    for li in list_items:
        info = li.find_element('class name', 'item-info-detail')
        item = {
            'title': li.find_element('tag name', 'h3').text,
            'price': float(li.find_element('class name', 'price-num').text.replace(',', '')),
            'price_sub': li.find_element('class name', 'sub-price').text,
            'address': li.find_element('tag name', 'span').text,
            'type': info.find_element('tag name', 'li').text,
            'age': float(info.find_elements('tag name', 'li')[1].text.replace('年', '')),
            'floor': info.find_elements('tag name', 'li')[2].text,
            '地': info.find_elements('tag name', 'li')[3].text,
            '實': info.find_elements('tag name', 'li')[4].text,
            '建': info.find_elements('tag name', 'li')[5].text,
            '格局': info.find_elements('tag name', 'li')[6].text,
            'url': li.find_element('tag name', 'a').get_attribute('href')
        }
        house_list.append(item)
    driver_c.close()
    return house_list


if __name__ == '__main__':
    region = '台北市'
    region_sub = ''
    budget_start = '1500'
    budget_end = '2500'
    age_start = ''
    age_end = '30'
    yungching_url = 'https://buy.yungching.com.tw'
    url = f'{yungching_url}/region/{region}-{region_sub}_c/{budget_start}-{budget_end}_price/{age_start}-{age_end}_age/'

    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get(url)

    url = driver.find_element('xpath', "//a[text()='最末頁']").get_attribute('href')
    max_page = int(url.split('=')[-1])
    url = url.split('=')[0] + '='
    urls = [url + str(i + 1) for i in range(max_page)]
    driver.close()

    p = Pool(int(cpu_count() * 0.8))
    result = p.map(page_proces, urls)
    p.close()
    p.join()

    result = [item for sublist in result for item in sublist]

    df = pd.DataFrame.from_dict(result)
