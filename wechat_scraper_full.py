from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from datetime import datetime
import pandas as pd
import time

# 设置ChromeDriver的路径
chromedriver_path = '/usr/local/bin/chromedriver'

# 初始化WebDriver
service = Service(chromedriver_path)
driver = webdriver.Chrome(service=service)

# 目标网址
url = 'https://mp.weixin.qq.com/mp/homepage?__biz=MzI0NDc0NzIyMw==&hid=1&sn=58c7f2d9e06b359a936ae7cf3d3888e6&scene=18&uin=&key=&devicetype=iMac19%2C2+OSX+OSX+11.4+build(20F71)&version=1308070c&lang=zh_CN&nettype=WIFI&ascene=7&session_us=gh_4f549e2b08b0&fontScale=100 '

# 访问目标网址
driver.get(url)

# 等待页面加载
time.sleep(5)

# 存储所有文章数据
all_articles = []

# 尝试切换所有可用的Tab
try:
    # 找到所有的Tab
    tabs = driver.find_elements(By.CSS_SELECTOR, '.jsCate')  # 根据实际CSS选择器调整

    for tab in tabs:
        # 显示 tab 名称
        print("tab: " + tab.text)
        tab.click()  # 点击Tab
        time.sleep(3)  # 等待页面加载

        # 爬取当前Tab页面上的文章标题和链接
        while True:
            # 滚动到页面底部
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)  # 等待新内容加载

            # 找到所有文章标题和链接
            titles = driver.find_elements(By.CSS_SELECTOR, '.js_title')  # 根据实际CSS选择器调整
            links = driver.find_elements(By.CSS_SELECTOR, '.js_post')  # 根据实际CSS选择器调整

            # 检查是否已经抓取过这些文章，如果没有则添加到列表
            new_articles = []
            for title, link in zip(titles, links):
                article_data = {
                    'Tab': tab.text,
                    'Title': title.text,
                    'Link': link.get_attribute('href')
                }
                if article_data not in all_articles:
                    new_articles.append(article_data)
                    
            # 如果没有新的文章，停止滚动
            if not new_articles:
                break

            # 将新文章添加到列表
            all_articles.extend(new_articles)
except Exception as e:
    print(f"发生错误：{e}")

finally:
    # 保存到Excel文件
    now = datetime.now().strftime('%Y%m%d%H%M%S')
    filename = f'微信_{now}.xlsx'
    df = pd.DataFrame(all_articles)
    df.to_excel(filename, index=False)

    # 关闭浏览器
    driver.quit()

print(f'爬取完成，数据已保存至 {filename}')