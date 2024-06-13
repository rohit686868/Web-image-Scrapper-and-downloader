import os
import requests
from PIL import Image
import logging
from bs4 import BeautifulSoup
from urllib.parse import unquote
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(filename='image_scraper.log', level=logging.ERROR)

def download_image(img_link, output_directory, index):
    try:
        img_data = requests.get(img_link, timeout=10).content
        extension = os.path.splitext(unquote(img_link))[1]

        if extension.lower() == '.svg':
            logging.error(f"Skipping SVG image: {img_link}")
            return

        with open(f"{output_directory}/{index}{extension}", 'wb') as f:
            f.write(img_data)

        img_path = f"{output_directory}/{index}{extension}"

        with Image.open(img_path) as img:
            img = img.convert("RGB")
            img.save(img_path, "JPEG")
            width, height = img.size

        with open(f"{output_directory}/{index}.txt", 'w') as meta_file:
            meta_file.write(f"Image {index} Metadata:\n")
            meta_file.write(f"Size: {os.path.getsize(img_path) / 1024:.2f} KB\n")
            meta_file.write(f"Resolution: {width}x{height}\n")
            meta_file.write(f"Format: JPEG\n")
    except Exception as e:
        logging.error(f"Failed to download image {index}: {e}")

def download_images_from_page(url, output_directory, page_number, num_images):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        image_links = [img['src'] for img in soup.find_all("img", {"src": True})]

        for index, img_link in enumerate(image_links[:num_images], start=1):
            download_image(img_link, output_directory, (page_number - 1) * num_images + index)

    except Exception as e:
        logging.error(f"An error occurred while processing page {page_number}: {e}")

def download_images_from_vecteezy(query, dir_name, num_images):
    output_directory = f'{dir_name}'
    os.makedirs(output_directory, exist_ok=True)

    base_url = f"https://www.vecteezy.com/free-photos/{query}/page/"
    total_downloaded = 0  

    try:
        with ThreadPoolExecutor(max_workers=5) as executor:
            page_number = 1
            while total_downloaded < num_images:
                url = base_url + str(page_number)
                downloaded_on_page = min(num_images - total_downloaded, 48)  
                executor.submit(download_images_from_page, url, output_directory, page_number, downloaded_on_page)
                total_downloaded += downloaded_on_page
                page_number += 1

                if downloaded_on_page < 48:
                    break  

    except Exception as e:
        logging.error(f"An error occurred: {e}")

if __name__ == "__main__":
    query = input("Enter the search query: ")
    dir_name = input("Enter the folder name: ")
    num_images = int(input("Enter the number of images to download: "))
    download_images_from_vecteezy(query, dir_name, num_images)
