from selenium.webdriver.common.by import By
from resources import *


def login_failed():
    try:
        oops_page = browser.find_element(By.XPATH, OOPS)
    except:
        oops_page = None
    finally:
        return bool(oops_page)
    
