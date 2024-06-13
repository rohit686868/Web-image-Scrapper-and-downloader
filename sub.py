from selenium import webdriver
from bs4 import BeautifulSoup
import requests as rq
import os
from urllib.parse import urlparse
import time
from PIL import Image

def download_images(num_images,query,fname):
    driver = webdriver.Chrome()
    link="https://www.pexels.com/search/" + query;
    driver.get(link)
    driver.implicitly_wait(10)

    output_directory = fname
    os.makedirs(output_directory, exist_ok=True)

    scroll_limit = (num_images // 30) + 1  # Assuming around 30 images load per scroll
    for _ in range(scroll_limit):
        # Scroll down to load more images
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2) 

    html_content = driver.page_source
    soup = BeautifulSoup(html_content, "html.parser")

    image_links = [img['src'] for img in soup.select('img[src^="https://images.pexels.com/photos"]')][:num_images]

    for index, img_link in enumerate(image_links, start=1):
        img_data = rq.get(img_link).content

        url_path = urlparse(img_link).path
        extension = os.path.splitext(url_path)[1]

        with open(f"{output_directory}/{index}{extension}", 'wb') as f:
            f.write(img_data)

        with open(f"{output_directory}/{index}.txt", 'w') as meta_file:
            meta_file.write(f"Image {index} Metadata:\n")

            with Image.open(f"{output_directory}/{index}{extension}") as img:
                width, height = img.size
                img_format = img.format

                meta_file.write(f"Size: {os.path.getsize(f'{output_directory}/{index}{extension}') / 1024:.2f} KB\n")
                meta_file.write(f"Resolution: {width}x{height}\n")
                meta_file.write(f"Format: {img_format}\n")

    driver.quit()

num_images = int(input("Enter the number of images to download: "))
query = input("Enter the search query: ")
fname = input("Enter the name of folder: ")
download_images(num_images,query,fname)
