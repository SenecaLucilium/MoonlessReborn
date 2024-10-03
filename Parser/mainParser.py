from articleParser import getArticleByHtml
from boostyParser import parsePeriod

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.webdriver import WebDriver
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

# from datetime import datetime
# creationDate = 'Sep 05 15:23'

# try:
#     creationDate_timestamp = int(datetime.strptime(creationDate, "%b %d %Y %H:%M").timestamp())
# except ValueError as e:
#     print(f"Ошибка при преобразовании даты: {e}")
#     creationDate += " 2024"
#     creationDate_timestamp = int(datetime.strptime(creationDate, "%b %d %H:%M %Y").timestamp())
# except ValueError as e:
#     print(f"Ошибка при преобразовании даты: {e}")

# print (creationDate_timestamp)
import json

options = Options()

driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=options)
# service = Service(executable_path='/snap/bin/geckodriver')
# driver = webdriver.Firefox(service=service, options=options)

inputing = input()
articles = parsePeriod ("06.05.2022", "03.10.2024", driver)

articles_dict = [article.__dict__ for article in articles]

# Преобразование в JSON
articles_json = json.dumps(articles_dict, ensure_ascii=False, indent=4)

# Запись JSON в файл
with open('articles.json', 'w', encoding='utf-8') as file:
    file.write(articles_json)

print("Файл articles.json успешно создан!")