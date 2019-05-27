from time import sleep
from pyquery import PyQuery as pq
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver import ActionChains
from selenium.common.exceptions import TimeoutException
from config import *
import  json
import  pymongo
client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]



browser = webdriver.Chrome()
browser.set_window_size(1920, 1080)
url='https://www.lagou.com/'
wait = WebDriverWait(browser,20)


def search():
    try:
        browser.get(url)
        actions = ActionChains(browser)
        actions.click()
        actions.perform()
        input = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.ID,'search_input'))
        )
        submit = WebDriverWait(browser,10).until(
            EC.element_to_be_clickable((By.ID,'search_button'))
        )
        # sleep(3000);
        sleep(2)
        input.send_keys('JAVA')
        sleep(2)
        submit.click()
    except TimeoutException:
        return search()

def next_page():
    try:
        next = WebDriverWait(browser,10).until(
            EC.element_to_be_clickable((By.XPATH,'//*[@id="s_position_list"]/div[2]/div/span[6]'))
        )
        next.click()
    except TimeoutException:
        next_page()


#获取数据以及对数据进行清洗
def get_salary():
    html = browser.page_source
    doc = pq(html)
    items = doc('.list_item_top').items()
    # print(items)
    java_list=[]

    for item in items:
        java_dict={
            'name':item.find('.p_top .position_link h3').text(),
            'salary':item.find('.p_bot .li_b_l').text().split(' ',1)[0],
            'qualification':item.find('.p_bot .li_b_l').text().split(' ',1)[1]
        }
        print(java_dict)
        java_list.append(java_dict)
    print(java_list)

    sleep(2)
    next_page()

#保存到MONGDB中
def save_data(result):
    try:
        if db[MONGO_COLLECTION].insert(result):
            print('存储到MONGODB成功')
    except Exception:
        print('存储到MONGODB失败')

#保存到json中
def save_json(dict):
    json_str = json.dumps(dict)
    with open('java_salary.json','w',encoding='utf-8') as json_file:
        json_file.write(json_str)



def main():
    search()
    for i in range(1,31):
        get_salary()

if __name__ == '__main__':
    main()

