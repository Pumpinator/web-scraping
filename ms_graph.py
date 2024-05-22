from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv

import json
import os
import msal

load_dotenv()

GRAPH_API_ENDPOINT = 'https://graph.microsoft.com/v1.0'
APP_ID = os.getenv('APP_ID')
SCOPES = ['Files.ReadWrite']
EMAIL = os.getenv('EMAIL')
PASSWORD = os.getenv('PASSWORD')

# Fuente: https://learndataanalysis.org/ms_graph-py-source-code/
def generate_access_token(service):
    # Save Session Token as a token file
    access_token_cache = msal.SerializableTokenCache()

    # read the token file
    if os.path.exists('ms_graph_api_token.json'):
        access_token_cache.deserialize(open("ms_graph_api_token.json", "r").read())
        token_detail = json.load(open('ms_graph_api_token.json',))
        token_detail_key = list(token_detail['AccessToken'].keys())[0]
        token_expiration = datetime.fromtimestamp(int(token_detail['AccessToken'][token_detail_key]['expires_on']))
        if datetime.now() > token_expiration:
            os.remove('ms_graph_api_token.json')
            access_token_cache = msal.SerializableTokenCache()

    # assign a SerializableTokenCache object to the client instance
    client = msal.PublicClientApplication(client_id=APP_ID, token_cache=access_token_cache)

    accounts = client.get_accounts()
    if accounts:
        # load the session
        token_response = client.acquire_token_silent(SCOPES, accounts[0])
    else:
        # authenticate your account as usual
        flow = client.initiate_device_flow(scopes=SCOPES)
        user_code = flow['user_code']
        print(user_code)


        chrome_options = webdriver.ChromeOptions()
        driver = webdriver.Remote(service=service, options=chrome_options)
        driver.get('https://microsoft.com/devicelogin')

        driver.find_element(By.XPATH, '/html/body/div/form/div/div/div[1]/div[3]/div/div/div/div[4]/div/input').send_keys(user_code)
        driver.find_element(By.XPATH, '/html/body/div/form/div/div/div[1]/div[3]/div/div/div/div[5]/div/div/div/input').click()
        
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '/html/body/div/form[1]/div/div/div[2]/div[1]/div/div/div/div/div[1]/div[3]/div/div/div//div[3]/div[2]/div/input[1]')))
        
        driver.find_element(By.XPATH, '/html/body/div/form[1]/div/div/div[2]/div[1]/div/div/div/div/div[1]/div[3]/div/div/div/div[3]/div[2]/div/input[1]').send_keys(EMAIL)
        driver.find_element(By.XPATH, '/html/body/div/form[1]/div/div/div[2]/div[1]/div/div/div/div/div[1]/div[3]/div/div/div/div[5]/div/div/div/div[2]/input').click()
        
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '/html/body/div/form[1]/div/div/div[2]/div[1]/div/div/div/div/div/div[3]/div/div[2]/div/div[3]/div/div[2]/input')))
        
        driver.find_element(By.XPATH, '/html/body/div/form[1]/div/div/div[2]/div[1]/div/div/div/div/div/div[3]/div/div[2]/div/div[3]/div/div[2]/input').send_keys(PASSWORD)
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div/form[1]/div/div/div[2]/div[1]/div/div/div/div/div/div[3]/div/div[2]/div/div[5]/div/div/div/div/input')))
        driver.find_element(By.XPATH, '/html/body/div/form[1]/div/div/div[2]/div[1]/div/div/div/div/div/div[3]/div/div[2]/div/div[5]/div/div/div/div/input').click()
        
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div/form/div/div/div[2]/div[1]/div/div/div/div/div/div[2]/div/div[2]/div/div[3]/div/div/div/div[2]/input')))
        driver.find_element(By.XPATH, '/html/body/div/form/div/div/div[2]/div[1]/div/div/div/div/div/div[2]/div/div[2]/div/div[3]/div/div/div/div[2]/input').click()

        token_response = client.acquire_token_by_device_flow(flow)
        
        driver.quit()

    with open('ms_graph_api_token.json', 'w') as _f:
        _f.write(access_token_cache.serialize())

    return token_response


if __name__ == '__main__':
    ...
