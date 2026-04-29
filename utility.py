from time import sleep
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import wait
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from resources import CONNECTION_TIMEOUT, OOPS_MESSAGE, TIMEOUT, status_code, browser, CURRENTLY_IN_MEETING

def print_message(message, status):
    print(message , end=" ")
    if status == status_code.SUCCESS:
        print(u'\N{white heavy check mark}')
    elif status == status_code.LOADING:
        for i in range(2):
            print('.' , end ="")
            sleep(1)
            i+=1
        print('.')
    else:
        print(u'\N{cross mark}')


def wait_for_element_to_be_clickable(xpath, timeout = TIMEOUT):
    try:
        WebDriverWait(browser, timeout).until(EC.element_to_be_clickable((By.XPATH, xpath)))
    except TimeoutException:
        print_message(CONNECTION_TIMEOUT, status_code.FAILED)
        raise TimeoutException("Element not clickable within {} seconds: {}".format(timeout, xpath))
    except Exception as e:
        print_message(OOPS_MESSAGE, status_code.FAILED)
        raise e

import re

def get_current_participants():
    try:
        sleep(5)
        # Try to get count from the People button label
        roster_btn = browser.find_element(By.ID, "roster-button")
        label = roster_btn.get_attribute("aria-label")
        # Extract number from string like "People, 5 participants" or "Show participants (5)"
        match = re.search(r'(\d+)', label)
        if match:
            count = int(match.group(1))
            return count
    except:
        pass
        
    try:
        # Fallback to the old span if it exists
        count_elem = browser.find_element(By.XPATH, CURRENTLY_IN_MEETING)
        text = count_elem.get_attribute('innerText')
        match = re.search(r'(\d+)', text)
        if match:
            return int(match.group(1))
    except:
        pass
        
    # If we can't find it, return a high number to stay in the meeting safely
    return 999
