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
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from ms_graph import generate_access_token, GRAPH_API_ENDPOINT
from dotenv import load_dotenv

load_dotenv()

parser = argparse.ArgumentParser(description="Computrabajo job scraper")
parser.add_argument('--keywords', type=str, default='Programador Java', required=False, help='Job keywords')
parser.add_argument('--location', type=str, default='León, Guanajuato', required=False, help='Job location')
args = parser.parse_args()

keywords = args.keywords
job_location = args.location

chrome_options = webdriver.ChromeOptions()
prefs = {"profile.default_content_setting_values.notifications" : 2}
chrome_options.add_experimental_option("prefs",prefs)
driver = webdriver.Remote(command_executor=os.getenv('SELENIUM_COMPUTRABAJO_HOST'), options=chrome_options)

url = 'https://mx.computrabajo.com'
driver.get(url)

driver.find_element(By.XPATH, '/html/body/main/div[2]/div/div/div/div[1]/div/div[1]/form/input[2]').send_keys(keywords)
driver.find_element(By.XPATH, '/html/body/main/div[2]/div/div/div/div[1]/div/div[2]/form/input[2]').send_keys(job_location)
driver.find_element(By.XPATH, '/html/body/main/div[2]/div/div/div/div[1]/div/div[2]/form/input[2]').click()
try:
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '/html/body/main/div[2]/div/div/div/div[1]/div/div[2]/form/ul[1]/li/div/div')))
    job_location = driver.find_element(By.XPATH, '/html/body/main/div[2]/div/div/div/div[1]/div/div[2]/form/ul[1]/li/div/div').text
    driver.find_element(By.XPATH, '/html/body/main/div[2]/div/div/div/div[1]/div/div[2]/form/ul[1]/li/div/div').click()
except TimeoutException:
    pass

driver.find_element(By.XPATH, '//*[@id="search-button"]').click()

current_date = datetime.now()
date_str = current_date.strftime("%y-%m-%d")
file_name = f'{date_str}-{keywords}-{job_location}-Computrabajo.csv'
file_path = f'Computrabajo/{file_name}'

with open(file_path, 'w', newline = '', encoding ='utf-8') as csvfile:
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow(['profile', 'title', 'company', 'job_location', 'publish_date', 'link'])
    
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
    f'{GRAPH_API_ENDPOINT}/me/drive/items/root:/Scraping/{file_path}:/content',
    headers=headers,
    data=media_file,
)

print(response.json())