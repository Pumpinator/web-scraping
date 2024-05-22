import argparse
import re
import sys
import os
import requests
import csv
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from selenium import webdriver
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from ms_graph import generate_access_token, GRAPH_API_ENDPOINT
from dotenv import load_dotenv

load_dotenv()

parser = argparse.ArgumentParser(description="Indeed job scraper")
parser.add_argument('--keywords', type=str, default='Programador Java', required=False, help='Job keywords')
parser.add_argument('--location', type=str, default='León, Guanajuato', required=False, help='Job location')
args = parser.parse_args()

keywords = args.keywords
job_location = args.location

chrome_options = webdriver.ChromeOptions()
driver = webdriver.Remote(command_executor=os.getenv('SELENIUM_INDEED_HOST'), options=chrome_options)

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
date_str = current_date.strftime("%y-%m-%d")
file_name = f'{date_str}-{keywords}-{job_location}-Indeed.csv'
file_path = f'Indeed/{file_name}'

with open(file_path, 'w', newline = '', encoding ='utf-8') as csvfile:
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow(['title', 'company', 'location', 'text', 'salary', 'publish_date', 'link'])
    
    for job in jobs:
        title = job.find_element(By.XPATH, './/div/div/div/div/div/table/tbody/tr/td[1]/div[1]/h2/a').text
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
        
        try:
            salary_element = job.find_element(By.XPATH, './/div/div/div/div/div/table/tbody/tr/td[1]/div[3]/div[1]/div[1]/div')
            salary_original = salary_element.text.strip()
            # Comprobar si el salario tiene el símbolo "$"
            if '$' in salary_original:
                # Comprobar si el salariocontiene 'a' en lugar de un guion '-'
                if ' a ' in salary_original:
                    # Caso 2: Salario en forma de rango, ej. "$##,### a $##,###"
                    # Extraer los números del texto del salario
                    salary_numbers = re.findall(r'\d{1,3}(?:,\d{3})*', salary_original)
                    salary_min = int(salary_numbers[0].replace(',', ''))
                    salary_max = int(salary_numbers[1].replace(',', ''))

                    # Calcular el salario promedio
                    salary = (salary_min + salary_max) / 2
                else:
                    # Caso 3: Salario sin rango, ej. "$##,###"
                    # Eliminar el símbolo "$" y cualquier carácter que no sea dígito
                    salary = int(re.sub(r'[^\d]', '', salary_original))
            else:
                # Caso 1: Salario no especificado o no numérico
                # Asignar un valor predeterminado de 0 al salario
                salary = 0
        except NoSuchElementException:
            salary = None

        print(title, company, location, text, salary, publish_date, link)
        
        csv_writer.writerow([title, company, location, text, salary, publish_date, link])
    
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