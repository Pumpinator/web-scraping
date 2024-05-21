import argparse
import sys
import os
import requests
import re
import csv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from selenium import webdriver
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from ms_graph import generate_access_token, GRAPH_API_ENDPOINT

parser = argparse.ArgumentParser(description="Computrabajo job scraper")
parser.add_argument('--keywords', type=str, default='Programador Java', required=False, help='Job keywords')
parser.add_argument('--location', type=str, default='León, Guanajuato', required=False, help='Job location')
args = parser.parse_args()

keywords = args.keywords
job_location = args.location

chrome_options = Options()
prefs = {"profile.default_content_setting_values.notifications" : 2}
chrome_options.add_experimental_option("prefs",prefs)
chrome_options.add_argument("--disable-popups")

# Aqui se debe de poner la ruta donde se encuentra su chromedriver, puede ser un contenedor en un puerto local o el ejecutable del driver
service = Service('/opt/homebrew/Caskroom/chromedriver/125.0.6422.60/chromedriver-mac-arm64/chromedriver')
driver = webdriver.Chrome(service=service, options=chrome_options)

url = 'https://mx.computrabajo.com'
driver.get(url)

driver.find_element(By.XPATH, '/html/body/main/div[2]/div/div/div/div[1]/div/div[1]/form/input[2]').send_keys(keywords)
driver.find_element(By.XPATH, '/html/body/main/div[2]/div/div/div/div[1]/div/div[2]/form/input[2]').send_keys(job_location)
driver.find_element(By.XPATH, '/html/body/main/div[2]/div/div/div/div[1]/button').click()

current_date = datetime.now()
date_str = current_date.strftime("%m-%d-%y")
file_name = f'{date_str}-Computrabajo-{keywords}-{job_location}.csv'
file_path = f'./{file_name}'

with open(file_path, 'w', newline = '', encoding ='utf-8') as csvfile:
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow(['title', 'company', 'job_location', 'publish_date', 'link'])
    
    while True:
        jobs = driver.find_elements(By.XPATH, '/html/body/main/div[8]/div/div[2]/div[1]/article')

        for job in jobs:
            try:
                title = job.find_element(By.XPATH, './/h2/a').text
            except NoSuchElementException:
                title = None

            try:
                job_location = job.find_element(By.XPATH, './/p[2]').text
            except NoSuchElementException:
                job_location = None
                
            try:
                tags = job.find_element(By.XPATH, './/p[1]')
            except NoSuchElementException:
                tags = None
                
            match = re.search(r"^\d+,\d+\s*(.*)", tags.text)
            if match:
                company = match.group(1).strip()  # Elimina espacios en blanco al principio y al final
            else:
                company = ""
                            
            try:
                publish_date = job.find_element(By.XPATH, './/p[3]').text
            except NoSuchElementException:
                publish_date = None
                
            try:
                link = job.find_element(By.XPATH, './/h2/a').get_attribute('href')
            except NoSuchElementException:
                link = None
            
            print(title, company, job_location, publish_date, link)
                
            csv_writer.writerow([title, company, job_location, publish_date, link])

        try:
            next_page = driver.find_element(By.XPATH, '//span[@title="Siguiente"]')
            next_page.click()
        except NoSuchElementException:
            break
        
driver.quit()

access_token = generate_access_token(service)
headers = {
    'Authorization': 'Bearer ' + access_token['access_token']
}

with open(file_path, 'rb') as upload:
    media_file = upload.read()

response = requests.put(
    f'{GRAPH_API_ENDPOINT}/me/drive/items/root:/Scraping/{file_name}:/content',
    headers=headers,
    data=media_file,
)

print(response.json())