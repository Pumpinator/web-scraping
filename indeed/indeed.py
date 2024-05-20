from selenium import webdriver
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

import csv
import time

keywords = 'Programador Java'
job_location = 'León, Guanajuato'

# Aqui se debe de poner la ruta donde se encuentra su chromedriver, puede ser un contenedor en un puerto local o el ejecutable del driver
service = Service('/opt/homebrew/Caskroom/chromedriver/125.0.6422.60/chromedriver-mac-arm64/chromedriver')
driver = webdriver.Chrome(service = service)

url = 'https://mx.indeed.com'
driver.get(url)

WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div/div[1]/div/span/div[4]/div[2]/div/div/div/div/form/div/div[1]/div[1]/div/div/span/input')))
driver.find_element(By.XPATH, '/html/body/div/div[1]/div/span/div[4]/div[2]/div/div/div/div/form/div/div[1]/div[1]/div/div/span/input').send_keys(keywords)
driver.find_element(By.XPATH, '/html/body/div/div[1]/div/span/div[4]/div[2]/div/div/div/div/form/div/div[1]/div[3]/div/div/span/input').send_keys(job_location)
driver.find_element(By.XPATH, '/html/body/div/div[1]/div/span/div[4]/div[2]/div/div/div/div/form/div/div[2]/button').click()

jobs = driver.find_elements(By.XPATH, '/html/body/main/div/div[2]/div/div[5]/div/div[1]/div[5]/div/ul/li')

current_date = datetime.now()
date_str = current_date.strftime("%m-%d-%y")
filename = f'indeed-{date_str}.csv'

with open(filename, 'w', newline = '', encoding ='utf-8') as csvfile:
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow(['title', 'company', 'location', 'text', 'publish_date', 'link'])
    
    for job in jobs:
        title = job.find_element(By.XPATH, './/div/div/div/div/div/table/tbody/tr/td[1]/div[1]/h2/a/span').text
        company = job.find_element(By.XPATH, './/div/div/div/div/div/table/tbody/tr/td[1]/div[2]/div/span').text
        location = job.find_element(By.XPATH, './/div/div/div/div/div/table/tbody/tr/td[1]/div[2]/div/div').text
        
        tags = []
        if job.find_elements(By.XPATH, './/div/div/div/div/div/div[1]/div[2]/div[1]/div/ul/li')[0].text == '':
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