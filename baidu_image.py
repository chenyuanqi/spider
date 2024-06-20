import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service

# 设置 Chrome WebDriver 路径
driver_path = '/usr/local/bin/chromedriver'
save_folder = 'AIGC'

# 创建保存图片的文件夹
if not os.path.exists(save_folder):
    os.makedirs(save_folder)

# 启动浏览器
options = webdriver.ChromeOptions()
options.add_argument('--start-maximized')
service = Service(executable_path=driver_path)
driver = webdriver.Chrome(service=service, options=options)

try:
    # 打开百度图片搜索页面
    driver.get('https://image.baidu.com/')

    # 等待搜索框加载
    wait = WebDriverWait(driver, 10)
    search_box = wait.until(EC.presence_of_element_located((By.NAME, 'word')))

    # 输入关键字并搜索
    search_box.send_keys('AIGC')
    search_box.send_keys(Keys.RETURN)

    # 等待页面加载
    time.sleep(3)

    # 爬取图片
    image_count = 0
    while image_count < 100:
        # 找到所有图片元素
        images = driver.find_elements(By.CSS_SELECTOR, 'img.main_img')

        for img in images[image_count:]:
            if image_count >= 100:
                break

            src = img.get_attribute('src')
            if src:
                try:
                    # 下载图片
                    image_data = requests.get(src).content
                    with open(f'{save_folder}/{image_count + 1}.jpg', 'wb') as f:
                        f.write(image_data)
                    image_count += 1
                    print(f'下载第 {image_count} 张图片')
                except Exception as e:
                    print(f'下载图片失败: {e}')

        # 下滑页面以加载更多图片
        driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
        time.sleep(3)

finally:
    # 关闭浏览器
    driver.quit()