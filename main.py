from FrontEnd.BotAPI import BotAPI
from boostyLogin import boostyLogin

driver = boostyLogin()
if driver is not None:
    BotAPI(driver)
else:
    print("None")