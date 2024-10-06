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

from BackEnd.logger import ParserLogger
LOGGER = ParserLogger()
DATA_JSON = 'Data/data.json'

def driverInit() -> WebDriver | None:
    LOGGER.info ('Driver init.')
    try:
        with open(DATA_JSON, 'r') as file:
            geckodriver = json.load(file)['geckodriver']

        options = Options()
        if geckodriver == "":
            driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=options)
        else:
            options.add_argument("--headless")
            service = Service(executable_path=geckodriver)
            driver = webdriver.Firefox(service=service, options=options)

        LOGGER.info ('Driver instance created.')
        return driver
    except Exception as err:
        LOGGER.error (f'Error at creating driver instance: {err}')
        return None

def loginAttempt(driver: WebDriver) -> bool:
    LOGGER.info ('Login Attempts starting.')
    retries = 0
    maxRetries = 5

    while retries < maxRetries:
        LOGGER.info (f'Login attempt #{retries + 1}.')
        try:
            driver.get('https://boosty.to')
            LOGGER.info (f'Waiting for page to load.')
            WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/div[1]/div[2]/div[2]/button[2]'))
            ).click()
            LOGGER.info (f'Clicked on LogIn button.')
            WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/div[4]/div/section/div/div/div[3]/button'))
            ).click()
            LOGGER.info (f'Clicked on login by phone, getting phone number.')

            with open(DATA_JSON, 'r') as file:
                phone = json.load(file)['phone']

            time.sleep(1)
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="root"]/div/div[4]/div/section/div/div/div[1]/form/div[1]/div[1]/div[1]/div/input'))
            ).send_keys(phone)
            time.sleep(1)
            WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="root"]/div/div[4]/div/section/div/div/div[1]/form/div[2]/button'))
            ).click()
            LOGGER.info (f'Clicked on Send Code button.')

            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="root"]/div/div[4]/div/section/div/div/div[1]/div[2]/div/div[1]')))
            LOGGER.info ("Waiting for the user to answer.")
            phoneCode = input("Введите 6-ти значный код с SMS и нажмите Enter:")
            LOGGER.info ("User answered.")
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="root"]/div/div[4]/div/section/div/div/div[1]/div[2]/div/div[1]/div[1]/div/input'))
            ).send_keys(phoneCode)
            LOGGER.info ("Sended keys.")
            time.sleep(5)

            driver_name = driver.find_element(By.CSS_SELECTOR, 'div.MiniProfile_name__2xYu[data-test-id="COMMON_MINIPROFILE:NAME"]').text
            with open(DATA_JSON, 'r') as file:
                name = json.load(file)['nickname']

            if driver_name == name:
                return True
            else:
                raise NoSuchElementException
        except NoSuchElementException:
            retries += 1
        except Exception as error:
            LOGGER.warning (f"Error happening while boosty tries with warning: {error}.")
            retries += 1
    return False

def boostyLogin() -> WebDriver | None:
    driver = driverInit()
    if driver is None:
        return None
    if loginAttempt(driver):
        LOGGER.info('Auth done - Driver is ready.')
        return driver
    else:
        return None