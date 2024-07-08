# -*- coding: utf-8 -*-
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def get_final_url_and_id(original_url):
    """模拟用户点击获取最终跳转地址，并提取ID。

    Args:
        original_url: 原始链接地址.

    Returns:
        一个包含最终URL和提取ID的字典，如果发生错误则返回None.
    """

    # 设置 Chrome 选项以无头模式运行
    chrome_options = Options()
    chrome_options.add_argument("--headless")

    # 初始化 Chrome WebDriver
    driver = webdriver.Chrome(options=chrome_options)

    try:
        # 从原始地址中提取ID
        match = re.search(r'id=(\d+)', original_url)
        if match:
            original_id = match.group(1)
        else:
            original_id = None

        # 打开原始链接
        driver.get(original_url)

        # 获取最终跳转地址
        final_url = driver.current_url

        # 从最终地址中提取ID
        match = re.search(r'id=(\d+)', final_url)
        if match:
            extracted_id = match.group(1)
        else:
            extracted_id = None

        return {
            'original_url': original_url,
            'final_url': final_url,
            'original_id': original_id,
            'extracted_id': extracted_id
        }
    except Exception as e:
        print("处理链接 '{}' 时发生错误: {}".format(original_url, e))
    finally:
        # 关闭浏览器
        driver.quit()


if __name__ == '__main__':
    # 测试链接列表
    url_list = [
        'https://uland.taobao.com/item/edetail?id=0bejZpwu7t8JYgYNdnS5d0h2t6-0N5d4NUBMM5Ga3wSn9',
        'https://uland.taobao.com/item/edetail?id=0GP5M7bi7t8JXG9P6XF5dei2t6-n68Bq6Uxrgq2pn7tz5',
        'https://uland.taobao.com/item/edetail?id=0kQ3D8Jt7t8Xbqg9DXs5Dgc2t6-770m67swKjmXJGPT0e',
    ]

    # 处理链接并打印结果
    for url in url_list:
        result = get_final_url_and_id(url)
        print(result)
