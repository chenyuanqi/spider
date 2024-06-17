import time
import datetime
import openpyxl
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

# 配置Chrome选项
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")  # 无头模式，不显示浏览器界面
chrome_options.add_argument("--disable-gpu")  # 禁用GPU加速

# 启动Chrome浏览器
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# Run：python3 wechat_scraper.py
# Before：pip3 install selenium openpyxl webdriver_manager

# 打开目标网站
driver.get("https://weixin.sogou.com/")

# 输入关键字 [AI]
search_box = driver.find_element(By.ID, "query")
search_box.send_keys("AI")

# 点击 [搜文章] 按钮
search_box.send_keys(Keys.RETURN)
time.sleep(3)  # 等待页面加载

# 创建一个新的Excel工作簿
wb = openpyxl.Workbook()
ws = wb.active
ws.title = "AI Articles"
ws.append(["Title", "Summary", "Link", "Source"])

# 爬取前5页
for page in range(1, 6):
    articles = driver.find_elements(By.XPATH, "//div[@class='txt-box']")
    
    for article in articles:
        title = article.find_element(By.XPATH, "./h3/a").text
        summary = article.find_element(By.XPATH, "./p").text
        link = article.find_element(By.XPATH, "./h3/a").get_attribute("href")
        source = article.find_element(By.XPATH, "./div[@class='s-p']/a").text
        
        ws.append([title, summary, link, source])
    
    # 翻页
    if page < 5:
        try:
            next_page = driver.find_element(By.XPATH, "//a[contains(text(), '下一页')]")
            next_page.click()
            time.sleep(5)  # 等待页面加载
        except NoSuchElementException:
            print(f"无法找到下一页按钮，在第 {page} 页停止爬取。")
            break

# 生成文件名
current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"AI_微信_{current_time}.xlsx"

# 保存Excel文件
wb.save(filename)
print(f"文件保存为: {filename}")

# 关闭浏览器
driver.quit()

