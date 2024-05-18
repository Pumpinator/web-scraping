from selenium import webdriver
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options

import csv

keyword = 'Programador Java'
location = 'León, Guanajuato'

chrome_options = Options()
prefs = {"profile.default_content_setting_values.notifications" : 2}
chrome_options.add_experimental_option("prefs",prefs)
chrome_options.add_argument("--disable-popups")

service = Service('/opt/homebrew/Caskroom/chromedriver/125.0.6422.60/chromedriver-mac-arm64/chromedriver')
driver = webdriver.Chrome(service=service, options=chrome_options)
url = 'https://mx.computrabajo.com'
driver.get(url)

driver.find_element(By.XPATH, '/html/body/main/div[2]/div/div/div/div[1]/div/div[1]/form/input[2]').send_keys(keyword)
driver.find_element(By.XPATH, '/html/body/main/div[2]/div/div/div/div[1]/div/div[2]/form/input[2]').send_keys(location)
driver.find_element(By.XPATH, '/html/body/main/div[2]/div/div/div/div[1]/button').click()

current_date = datetime.now()
date_str = current_date.strftime("%m-%d-%y")
filename = f'computrabajo-{date_str}.csv'

with open(filename, 'w', newline = '', encoding ='utf-8') as csvfile:
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow(['title', 'location', 'publish_date', 'link'])
    
    while True:
        jobs = driver.find_elements(By.XPATH, '/html/body/main/div[8]/div/div[2]/div[1]/article')
        print(len(jobs))

        for job in jobs:
            try:
                title = job.find_element(By.XPATH, './/h2/a').text
            except NoSuchElementException:
                title = None

            try:
                location = job.find_element(By.XPATH, './/p[2]').text
            except NoSuchElementException:
                location = None
                
            try:
                publish_date = job.find_element(By.XPATH, './/p[3]').text
            except NoSuchElementException:
                publish_date = None
                
            try:
                link = job.find_element(By.XPATH, './/h2/a').get_attribute('href')
            except NoSuchElementException:
                link = None
            
            print(title, location, publish_date, link)
                
            csv_writer.writerow([title, location, publish_date, link])

        try:
            next_page = driver.find_element(By.XPATH, '//span[@title="Siguiente"]')
            next_page.click()
        except NoSuchElementException:
            break
        
driver.quit()