import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import pandas as pd
from datetime import datetime

# Run: python3 wechat_scraper.py

# 设置 WebDriver 路径
# 如果没有安装，brew install --cask chromedriver
webdriver_path = '/usr/local/bin/chromedriver'  # 替换为你的 WebDriver 路径

# 初始化浏览器
service = Service(webdriver_path)
driver = webdriver.Chrome(service=service)
driver.get('https://weixin.sogou.com/')

# 输入关键字并搜索
search_box = driver.find_element(By.NAME, 'query')
search_box.send_keys('AI')
search_box.send_keys(Keys.RETURN)
time.sleep(2)  # 等待页面加载

# 爬取内容
results = []
for _ in range(5):
    articles = driver.find_elements(By.XPATH, '//ul[@class="news-list"]/li')
    for article in articles:
        title = article.find_element(By.XPATH, './/h3/a').text
        summary = article.find_element(By.XPATH, './/p[@class="txt-info"]').text
        link = article.find_element(By.XPATH, './/h3/a').get_attribute('href')
        source = article.find_element(By.XPATH, './/div[@class="s-p"]/span').text
        results.append([title, summary, link, source])
    
    # 翻页
    next_button = driver.find_element(By.ID, 'sogou_next')
    next_button.click()
    time.sleep(5)  # 休眠5秒

# 保存到Excel文件
df = pd.DataFrame(results, columns=['标题', '摘要', '链接', '来源'])
filename = f'AI_微信_{datetime.now().strftime("%Y%m%d%H%M%S")}.xlsx'
df.to_excel(filename, index=False)

# 关闭浏览器
driver.quit()
