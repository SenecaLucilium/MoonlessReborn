import time
import json
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.webdriver import WebDriver
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

from BackEnd.logger import Logger
logger = Logger()

def driverInit() -> WebDriver | None:
    logger.logger.info ('Driver init.')
    try:
        options = Options()
        options.add_argument("--headless")
        logger.logger.info ('Options for driver init.')

        driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=options)
        # service = Service(executable_path='/snap/bin/geckodriver')
        # driver = webdriver.Firefox(service=service, options=options)
        logger.logger.info ('Driver instance created.')
        return driver
    except Exception as err:
        logger.logger.error (f'Error at creating driver instance: {err}')
        return None

def loginAttempt(driver: WebDriver) -> bool:
    logger.logger.info ('Login Attempts starting.')
    retries = 0
    maxRetries = 10

    while retries < maxRetries:
        logger.logger.info (f'Login attempt #{retries + 1}.')
        try:
            driver.get('https://boosty.to')

            WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="topMenu"]/div[3]/div/button[2]'))
            ).click()
            WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="root"]/div/div[4]/div/section/div/div/div[3]/button'))
            ).click()

            with open('data.json', 'r') as file:
                phone = json.load(file)['phone']

            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="root"]/div/div[4]/div/section/div/div/div[1]/form/div[1]/div[1]/div[1]/div/input'))
            ).send_keys(phone)
            WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="root"]/div/div[4]/div/section/div/div/div[1]/form/div[2]/button'))
            ).click()

            time.sleep(5)
            element = driver.find_element(By.XPATH, '//*[@id="root"]/div/div[4]/div/section/div/div/div[1]/div[2]/div/div[1]')
            logger.logger.info ("Waiting for the user to answer.")
            phoneCode = input("Введите 6-ти значный код с SMS и нажмите Enter:")
            logger.logger.info ("User answered.")
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="root"]/div/div[4]/div/section/div/div/div[1]/div[2]/div/div[1]/div[1]/div/input'))
            ).send_keys(phoneCode)
            time.sleep(5)

            driver_name = driver.find_element(By.CSS_SELECTOR, 'div.MiniProfile_name__2xYu[data-test-id="COMMON_MINIPROFILE:NAME"]').text
            with open('data.json', 'r') as file:
                name = json.load(file)['nickname']

            if driver_name == name:
                return True
            else:
                raise NoSuchElementException
        except NoSuchElementException:
            retries += 1
        except Exception as err:
            retries += 1
    return False

def boostyLogin() -> WebDriver | None:
    driver = driverInit()
    if driver is None:
        return None
    if loginAttempt(driver):
        logger.logger.info('Auth done - Driver is ready.')
        return driver
    else:
        return None