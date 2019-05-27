from time import sleep
from pyquery import PyQuery as pq
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver import ActionChains
from selenium.common.exceptions import TimeoutException
from config import *
import pymongo


client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]


class LagouSpider(object):
    def __init__(self):
        self.url = 'https://www.lagou.com/'
        self.browser = webdriver.Chrome()
        self.browser.set_window_size(1920, 1080)
        self.wait = WebDriverWait(self.browser,20)
        self.list=[]


    def search(self):
        try:
            self.browser.get(self.url)
            actions = ActionChains(self.browser)
            actions.click()
            actions.perform()
            input = WebDriverWait(self.browser, 10).until(
                EC.presence_of_element_located((By.ID,'search_input'))
            )
            submit = WebDriverWait(self.browser,10).until(
                EC.element_to_be_clickable((By.ID,'search_button'))
            )

            sleep(2)
            input.send_keys('JAVA')
            sleep(2)
            submit.click()
        except TimeoutException:
            return self.search()

    def next_page(self):
        try:
            next = WebDriverWait(self.browser,10).until(
                EC.element_to_be_clickable((By.CLASS_NAME,'pager_next '))
            )
            next.click()
        except TimeoutException:
            self.next_page()


    #获取数据以及对数据进行清洗
    def get_salary(self):
        html = self.browser.page_source
        doc = pq(html)
        items = doc('.list_item_top').items()
        for item in items:
            java_dict={
                'position':item.find('.p_top .position_link h3').text(),
                'salary':item.find('.p_bot .li_b_l').text().split(' ',1)[0],
                'qualification':item.find('.p_bot .li_b_l').text().split(' ',1)[1]
            }
            print(java_dict)
            self.list.append(java_dict)

            self.save_data(java_dict)
        print(len(self.list))
        sleep(2)

        self.next_page()


    #保存到MONGDB中
    def save_data(self,result):
        try:
            if db[MONGO_COLLECTION].insert(result):
                print('存储到MONGODB成功')
        except Exception:
            print('存储到MONGODB失败')

    def main(self):
        self.search()
        for i in range(1,31):
            self.get_salary()


LagouSpider().main()

