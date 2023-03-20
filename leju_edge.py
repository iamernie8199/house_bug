import pandas as pd
from selenium import webdriver
from tqdm import tqdm
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service

from webdriver_manager.microsoft import EdgeChromiumDriverManager

city = {
    '台北市': 'A'
}
building = {
    '大樓': '',
    '透天': 3,
    '公寓': 4
}
budget_start = '1500'
budget_end = '2500'
# 屋齡 -1=預售
age_start = '-1'
age_end = '30'
url = f"https://www.leju.com.tw/community?city={city['台北市']}&area=all&building_type={building['大樓']}&budget_price={budget_start}_{budget_end}&house_age=-1_30"

driver = webdriver.Edge(service=Service(EdgeChromiumDriverManager().install()))
driver.get(url)