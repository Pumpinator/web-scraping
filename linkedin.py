import argparse
import re
import sys
import os
import requests
import csv
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException
from ms_graph import generate_access_token, GRAPH_API_ENDPOINT

parser = argparse.ArgumentParser(description="LinkedIn job scraper")
parser.add_argument('--keywords', type=str, default='Programador Java', required=False, help='Job keywords')
parser.add_argument('--location', type=str, default='León, Guanajuato', required=False, help='Job location')
args = parser.parse_args()

keywords = args.keywords
job_location = args.location

options = webdriver.ChromeOptions()
driver = webdriver.Remote(command_executor='http://localhost:4444/wd/hub', options=options)

url = 'https://www.linkedin.com/jobs/search?trk=guest_homepage-basic_guest_nav_menu_jobs'
driver.get(url)

driver.find_element(By.XPATH, '/html/body/div[1]/header/nav/section/section[2]/form/section[1]/input').send_keys(keywords)
driver.find_element(By.XPATH, '/html/body/div[1]/header/nav/section/section[2]/form/section[2]/input').clear()
driver.find_element(By.XPATH, '/html/body/div[1]/header/nav/section/section[2]/form/section[2]/input').send_keys(job_location)
driver.find_element(By.XPATH, '/html/body/div[1]/header/nav/section/section[2]/form/button').click()

SCROLL_PAUSE_TIME = 2

last_height = driver.execute_script("return document.body.scrollHeight")

while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    time.sleep(SCROLL_PAUSE_TIME)

    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

jobs = driver.find_elements(By.XPATH, '//*[@id="main-content"]/section[2]/ul/li')

current_date = datetime.now()
date_str = current_date.strftime("%y-%m-%d")
file_name = f'{date_str}-{keywords}-{job_location}-LinkedIn.csv'
file_path = f'./web-scraping/data/LinkedIn{file_name}'

with open(file_path, 'w', newline = '', encoding ='utf-8') as csvfile:
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow(['title', 'company', 'location', 'text', 'publish_date', 'link'])

    for job in jobs:
        title = job.find_element(By.CLASS_NAME, 'base-search-card__title').text

        try:
            company = job.find_element(By.CLASS_NAME, 'hidden-nested-link').text
        except NoSuchElementException:
            company = None

        location = job.find_element(By.CLASS_NAME, 'job-search-card__location').text

        try:
            text = job.find_element(By.CLASS_NAME, 'job-posting-benefits__text').text
        except NoSuchElementException:
            text = None

        try:
            publish_date = job.find_element(By.CLASS_NAME, 'job-search-card__listdate').get_attribute('datetime')
        except NoSuchElementException:
            text = None

        try:
            link = job.find_element(By.CLASS_NAME, 'base-card__full-link').get_attribute('href')
        except NoSuchElementException:
            link = None
        
        print(title, company, location, text, publish_date, link)
        
        csv_writer.writerow([title, company, location, text, publish_date, link])

access_token = generate_access_token(driver)
headers = {
    'Authorization': 'Bearer ' + access_token['access_token']
}

with open(file_path, 'rb') as upload:
    media_file = upload.read()

response = requests.put(
    f'{GRAPH_API_ENDPOINT}/me/drive/items/root:/Scraping/LinkedIn/{file_name}:/content',
    headers=headers,
    data=media_file,
)

print(response.json())