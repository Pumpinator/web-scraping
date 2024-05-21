import argparse
import sys
import os
import requests
import csv
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from selenium import webdriver
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from ms_graph import generate_access_token, GRAPH_API_ENDPOINT

parser = argparse.ArgumentParser(description="Indeed job scraper")
parser.add_argument('--keywords', type=str, default='Programador Java', required=False, help='Job keywords')
parser.add_argument('--location', type=str, default='León, Guanajuato', required=False, help='Job location')
args = parser.parse_args()

keywords = args.keywords
job_location = args.location

# Aqui se debe de poner la ruta donde se encuentra su chromedriver, puede ser un contenedor en un puerto local o el ejecutable del driver
service = Service('/opt/homebrew/Caskroom/chromedriver/125.0.6422.60/chromedriver-mac-arm64/chromedriver')
driver = webdriver.Chrome(service = service)

url = 'https://mx.indeed.com'
driver.get(url)

WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div/div[1]/div/span/div[4]/div[2]/div/div/div/div/form/div/div[1]/div[1]/div/div/span/input')))
driver.find_element(By.XPATH, '/html/body/div/div[1]/div/span/div[4]/div[2]/div/div/div/div/form/div/div[1]/div[1]/div/div/span/input').send_keys(keywords)
driver.find_element(By.XPATH, '/html/body/div/div[1]/div/span/div[4]/div[2]/div/div/div/div/form/div/div[1]/div[3]/div/div/span/input').send_keys(job_location)
driver.find_element(By.XPATH, '/html/body/div/div[1]/div/span/div[4]/div[2]/div/div/div/div/form/div/div[1]/div[3]/div/div/span/input').click()
try:
    time.sleep(0.5)
    job_location = driver.find_element(By.ID, 'combobox-where-list').find_element(By.XPATH, './/a[1]').find_element(By.XPATH, './/div[2]/div').text
    driver.find_element(By.ID, 'combobox-where-list').find_element(By.XPATH, './/a[1]').click()
    time.sleep(0.5)
except NoSuchElementException:
    pass
driver.find_element(By.XPATH, '/html/body/div/div[1]/div/span/div[4]/div[2]/div/div/div/div/form/div/div[2]/button').click()

jobs = driver.find_elements(By.XPATH, '/html/body/main/div/div[2]/div/div[5]/div/div[1]/div[5]/div/ul/li')

current_date = datetime.now()
date_str = current_date.strftime("%m-%d-%y")
file_name = f'{date_str}-Indeed-{keywords}-{job_location}.csv'
file_path = f'./{file_name}'

with open(file_path, 'w', newline = '', encoding ='utf-8') as csvfile:
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow(['title', 'company', 'location', 'text', 'publish_date', 'link'])
    
    for job in jobs:
        title = job.find_element(By.XPATH, './/div/div/div/div/div/table/tbody/tr/td[1]/div[1]/h2/a/span').text
        company = job.find_element(By.XPATH, './/div/div/div/div/div/table/tbody/tr/td[1]/div[2]/div/span').text
        location = job.find_element(By.XPATH, './/div/div/div/div/div/table/tbody/tr/td[1]/div[2]/div/div').text
        
        tags = []
        if job.find_elements(By.XPATH, './/div/div/div/div/div/div[1]/div[2]/div[1]/div/ul/li')[0] and job.find_elements(By.XPATH, './/div/div/div/div/div/div[1]/div[2]/div[1]/div/ul/li')[0].text == '':
            print('No tags')
            tags.append(job.find_element(By.XPATH, './/div/div/div/div/div/div[1]/div/div[1]/div').text)
        else:
            print('Tags')
            for tag in job.find_elements(By.XPATH, './/div/div/div/div/div/div[1]/div[2]/div[1]/div/ul/li'):
                tags.append(tag.text)
        text = ' '.join(tags)    
        
        try:
            publish_date = job.find_element(By.XPATH, './/div/div/div/div/div/div[1]/div[2]/div[1]/span[1]').text
        except NoSuchElementException:
            publish_date = job.find_element(By.XPATH, './/div/div/div/div/div/div[1]/div/div[1]/span[1]').text
        
        link = job.find_element(By.XPATH, './/div/div/div/div/div/table/tbody/tr/td[1]/div[1]/h2/a').get_attribute('href')
        
        print(title, company, location, text, publish_date, link)
        
        csv_writer.writerow([title, company, location, text, publish_date, link])
    
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