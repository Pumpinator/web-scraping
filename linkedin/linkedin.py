from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException

import csv
import time

service = Service('/opt/homebrew/Caskroom/chromedriver/125.0.6422.60/chromedriver-mac-arm64/chromedriver')

driver = webdriver.Chrome(service = service)

url = 'https://www.linkedin.com/jobs/search?keywords=Programador%20Java&location=Le%C3%B3n%2C%20Guanajuato%2C%20Mexico&geoId=101221629&trk=public_jobs_jobs-search-bar_search-submit&position=1&pageNum=0'
driver.get(url)

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

with open('linkedin.csv', 'w', newline = '', encoding ='utf-8') as csvfile:
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow(['title', 'location', 'text', 'publish_date', 'link'])

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

        publish_date = job.find_element(By.CLASS_NAME, 'job-search-card__listdate').get_attribute('datetime')

        try:
            link = job.find_element(By.CLASS_NAME, 'base-card__full-link').get_attribute('href')
        except NoSuchElementException:
            link = None
        
        print(title, company, location, text, publish_date, link)
        
        csv_writer.writerow([title, location, text, publish_date, link])

driver.quit()