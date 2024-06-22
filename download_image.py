import requests
from bs4 import BeautifulSoup
import os
import base64
import re
from urllib.parse import urljoin
import cssutils
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
import logging

class ImageDownloader:
    def __init__(self, url):
        self.url = url
        self.session = requests.Session()
        self.soup = None

        # Configure cssutils logging
        cssutils.log.setLevel(logging.CRITICAL)

    def fetch(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        }
        response = requests.get(self.url, headers=headers)
        response.raise_for_status()
        self.soup = BeautifulSoup(response.text, 'html.parser')

    def save_image(self, img_url, save_folder):
        if img_url.startswith('data:image'):  # Handle data URLs separately
            self.save_data_uri_image(img_url, save_folder)
            return

        try:
            img_response = self.session.get(img_url)
            img_response.raise_for_status()  # Ensure the response status code is 200
            img_name = os.path.basename(img_url)
            with open(os.path.join(save_folder, img_name), 'wb') as f:
                f.write(img_response.content)
        except requests.exceptions.HTTPError as e:
            print(f"HTTP error occurred while downloading {img_url}: {e}")
        except requests.exceptions.RequestException as e:
            print(f"Error downloading {img_url}: {e}")

    def save_data_uri_image(self, data_uri, save_folder):
        try:
            header, encoded = data_uri.split(",", 1)
            # Fix base64 string length
            encoded = self.fix_base64_padding(encoded)
            data = base64.b64decode(encoded)
            mime_type = header.split(";")[0].split(":")[1]
            extension = mime_type.split("/")[1]
            img_name = f"image.{extension}"
            with open(os.path.join(save_folder, img_name), 'wb') as f:
                f.write(data)
        except Exception as e:
            print(f"Error saving data URI image: {e}")

    def fix_base64_padding(self, encoded):
        # Fix base64 string length
        missing_padding = len(encoded) % 4
        if missing_padding:
            encoded += '=' * (4 - missing_padding)
        return encoded

    def download_img_tags(self, save_folder='downloaded_images'):
        if not os.path.exists(save_folder):
            os.makedirs(save_folder)

        for img_tag in self.soup.find_all('img'):
            img_url = img_tag.get('src')
            if img_url:
                full_url = urljoin(self.url, img_url)
                self.save_image(full_url, save_folder)

    def download_css_images(self, save_folder='downloaded_images'):
        if not os.path.exists(save_folder):
            os.makedirs(save_folder)

        # Find all <link> elements that link to CSS files
        for link in self.soup.find_all('link', {'rel': 'stylesheet', 'href': True}):
            css_url = urljoin(self.url, link['href'])
            try:
                css_response = self.session.get(css_url)
                css_response.raise_for_status()
                self.parse_css(css_response.text, save_folder)
            except requests.RequestException as e:
                print(f"Failed to download CSS file {css_url}: {e}")

        # Also check inline styles in <style> tags
        for style in self.soup.find_all('style'):
            self.parse_css(style.text, save_folder)

    def parse_css(self, css_text, save_folder):
        stylesheet = cssutils.parseString(css_text)
        for rule in stylesheet:
            if rule.type == rule.STYLE_RULE:
                bg_image = rule.style.getProperty('background-image')
                if bg_image and 'url(' in bg_image.cssText:
                    image_urls = re.findall(r'url\((.*?)\)', bg_image.cssText)
                    for img_url in image_urls:
                        img_url = img_url.strip('"').strip("'")
                        if img_url:  # Ignore empty URLs
                            full_url = urljoin(self.url, img_url)
                            self.save_image(full_url, save_folder)

    def download_svg_images(self, save_folder='downloaded_images'):
        if not os.path.exists(save_folder):
            os.makedirs(save_folder)

        svg_tags = self.soup.find_all('svg')
        for index, svg in enumerate(svg_tags):
            svg_str = str(svg)
            svg_file_path = os.path.join(save_folder, f'svg_image_{index}.svg')
            with open(svg_file_path, 'w') as file:
                file.write(svg_str)

    def download_data_uri_images(self, save_folder='downloaded_images'):
        if not os.path.exists(save_folder):
            os.makedirs(save_folder)

        for img_tag in self.soup.find_all('img'):
            img_url = img_tag.get('src')
            if img_url and img_url.startswith('data:image'):
                self.save_data_uri_image(img_url, save_folder)

    def download_canvas_images(self, save_folder='downloaded_images'):
        if not os.path.exists(save_folder):
            os.makedirs(save_folder)

        # Setup WebDriver
        service = Service(ChromeDriverManager().install())
        options = webdriver.ChromeOptions()
        options.headless = True  # Use headless mode
        driver = webdriver.Chrome(service=service, options=options)

        try:
            driver.get(self.url)
            time.sleep(5)  # Wait for JavaScript to render

            # Find all canvas elements
            canvases = driver.find_elements(By.TAG_NAME, "canvas")
            for index, canvas in enumerate(canvases):
                # Get base64 encoded image data from Canvas
                canvas_base64 = driver.execute_script("return arguments[0].toDataURL('image/png').substring(21);", canvas)
                canvas_png = base64.b64decode(self.fix_base64_padding(canvas_base64))
                canvas_file_path = os.path.join(save_folder, f'canvas_image_{index}.png')
                with open(canvas_file_path, 'wb') as f:
                    f.write(canvas_png)

        finally:
            driver.quit()

# Example usage
if __name__ == "__main__":
    downloader = ImageDownloader("https://unsplash.com/")
    downloader.fetch()
    downloader.download_img_tags()
    downloader.download_data_uri_images()
    downloader.download_css_images()
    downloader.download_svg_images()
    downloader.download_canvas_images()
