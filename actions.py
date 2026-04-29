from datetime import datetime
from validations import login_failed
from resources import *
from time import sleep
from selenium.webdriver.common.by import By
from utility import print_message, wait_for_element_to_be_clickable, get_current_participants


def try_again():
    print_message('Trying again', status_code.LOADING)
    browser.find_element(By.XPATH, TRY_AGAIN_BUTTON).click()
    wait_for_element_to_be_clickable(NEW_MEETING_BUTTON)
    

def wait_for_login():
    print_message('Please log in manually in the browser window...', status_code.LOADING)
    # Wait for the New Meeting button to appear (indicator of successful login/dashboard)
    # This will now raise an exception if it fails, stopping the script.
    wait_for_element_to_be_clickable(NEW_MEETING_BUTTON, timeout=600)
    sleep(2)
    print_message('Login detected! Automation taking over.', status_code.SUCCESS)


def join_via_link(link):
    print_message('Navigating to meeting link...', status_code.LOADING)
    browser.get(link)
    
    # Smarter detection: Is there a "Join now" or "Continue on browser" button?
    # We wait a bit for the page to redirect or show the choice
    seconds = 0
    while seconds < 20:
        # Check if we are already on the pre-join screen
        try:
            if browser.find_elements(By.XPATH, PREJOIN_JOIN_BUTTON) or browser.find_elements(By.XPATH, GUEST_NAME_FIELD):
                print_message('Pre-join screen detected!', status_code.SUCCESS)
                break
        except:
            pass
            
        # Check if we need to click "Continue on this browser"
        try:
            web_buttons = browser.find_elements(By.XPATH, USE_TEAMS_ON_WEB_BUTTON)
            if web_buttons:
                web_buttons[0].click()
                print_message('Clicked "Join on Web"', status_code.SUCCESS)
                sleep(5)
                break
        except:
            pass
            
        sleep(1)
        seconds += 1
    
    join_meeting()
    


def keep_finding(xpath, interval):
    element_not_found = True
    while element_not_found:
        try:
            element = browser.find_element(By.XPATH, xpath) 
            element_not_found = False
        except:    
            sleep(interval)
        else:
            return element 


def join_meeting():
    print_message('Time to meet. Joining ...', status_code.LOADING)
    sleep(10)
    
    # Fail-safe camera off
    try:
        camera_button = browser.find_element(By.XPATH, CAMERA_BUTTON)
        camera_button.click()
        print_message('Camera off', status_code.SUCCESS)
        sleep(2)
    except:
        print_message('Camera button skipped or not found', status_code.LOADING)

    # Fail-safe microphone off
    try:
        mic_button = browser.find_element(By.XPATH, MIC_BUTTON)
        mic_button.click()
        print_message('Microphone off', status_code.SUCCESS)
        sleep(2)
    except:
        print_message('Microphone button skipped or not found', status_code.LOADING)

    # Handle Guest Name Entry (if required)
    try:
        name_field = browser.find_element(By.XPATH, GUEST_NAME_FIELD)
        if name_field:
            name_field.send_keys("Zain") # Using user's name
            print_message('Guest name entered', status_code.SUCCESS)
            sleep(2)
    except:
        pass

    # Join Now
    try:
        wait_for_element_to_be_clickable(PREJOIN_JOIN_BUTTON, timeout=30)
        browser.find_element(By.XPATH, PREJOIN_JOIN_BUTTON).click()
        print_message('Join button clicked!', status_code.SUCCESS)
        print_message('Waiting for admission (Lobby or joining)...', status_code.LOADING)
        # Use a very long timeout (2 hours) to wait for the host to admit you
        wait_for_element_to_be_clickable(HANGUP_BUTTON, timeout=7200)
        print_message('Joined Meeting at {}'.format(datetime.now()) , status_code.SUCCESS)
    except Exception as e:
        print_message('Could not join meeting room. Check if you are stuck in lobby.', status_code.FAILED)
        raise e
    

def leave_meeting():
    browser.execute_script("document.getElementById('roster-button').click()")
    while get_current_participants() > MINIMUM_PARTICIPANTS:
        sleep(60)
    print_message('Leaving', status_code.LOADING)
    browser.execute_script("document.getElementById('hangup-button').click()")
    print_message('Left Meeting at {}'.format(datetime.now()) , status_code.SUCCESS)


          
