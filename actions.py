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
    

def dismiss_modals():
    """Attempts to click 'Got it', 'Dismiss', or other common Teams popups."""
    try:
        modals = browser.find_elements(By.XPATH, DISMISS_MODAL)
        for modal in modals:
            if modal.is_displayed():
                modal.click()
                print_message('Dismissed a modal popup', status_code.SUCCESS)
                sleep(1)
    except:
        pass

def wait_for_login():
    print_message('Please log in manually in the browser window...', status_code.LOADING)
    # Wait for the New Meeting button to appear (indicator of successful login/dashboard)
    # This will now raise an exception if it fails, stopping the script.
    wait_for_element_to_be_clickable(NEW_MEETING_BUTTON, timeout=600)
    sleep(2)
    print_message('Login detected! Automation taking over.', status_code.SUCCESS)


def join_via_link(link):
    # Check if we are already in a meeting
    try:
        if browser.find_elements(By.XPATH, HANGUP_BUTTON):
            print_message('Already in a meeting. Skipping navigation.', status_code.SUCCESS)
            return
    except:
        pass

    print_message('Navigating to meeting link...', status_code.LOADING)
    browser.get(link)
    
    # Smarter detection: Is there a "Join now" or "Continue on browser" button?
    # We wait a bit for the page to redirect or show the choice
    seconds = 0
    while seconds < 40: # Increased timeout
        dismiss_modals() # Keep dismissing annoying popups

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
                # Use JS click to bypass potential overlays
                browser.execute_script("arguments[0].click();", web_buttons[0])
                print_message('Clicked "Join on Web"', status_code.SUCCESS)
                sleep(5)
                # After clicking web join, we usually land on pre-join screen shortly
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
    # If already in meeting, skip
    try:
        if browser.find_elements(By.XPATH, HANGUP_BUTTON):
            return
    except:
        pass

    print_message('Time to meet. Joining ...', status_code.LOADING)
    sleep(5)
    dismiss_modals()
    sleep(5)
    
    # Fail-safe camera off
    try:
        camera_buttons = browser.find_elements(By.XPATH, CAMERA_BUTTON)
        if camera_buttons:
            camera_buttons[0].click()
            print_message('Camera off', status_code.SUCCESS)
            sleep(2)
    except:
        print_message('Camera button skipped or not found', status_code.LOADING)

    # Fail-safe microphone off
    try:
        mic_buttons = browser.find_elements(By.XPATH, MIC_BUTTON)
        if mic_buttons:
            mic_buttons[0].click()
            print_message('Microphone off', status_code.SUCCESS)
            sleep(2)
    except:
        print_message('Microphone button skipped or not found', status_code.LOADING)

    # Handle Guest Name Entry (if required)
    try:
        name_fields = browser.find_elements(By.XPATH, GUEST_NAME_FIELD)
        if name_fields:
            name_fields[0].send_keys("Zain Ul Abideen 2600531") # Using user's name
            print_message('Guest name entered', status_code.SUCCESS)
            sleep(2)
    except:
        pass

    # Join Now
    try:
        join_buttons = browser.find_elements(By.XPATH, PREJOIN_JOIN_BUTTON)
        if join_buttons:
            join_buttons[0].click()
            print_message('Join button clicked!', status_code.SUCCESS)
        
        print_message('Waiting for admission (Lobby or joining)...', status_code.LOADING)
        # Use a very long timeout (2 hours) to wait for the host to admit you
        wait_for_element_to_be_clickable(HANGUP_BUTTON, timeout=7200)
        print_message('Joined Meeting at {}'.format(datetime.now()) , status_code.SUCCESS)
    except Exception as e:
        # Check if we are already joined before raising error
        if not browser.find_elements(By.XPATH, HANGUP_BUTTON):
            print_message('Could not join meeting room. Check if you are stuck in lobby.', status_code.FAILED)
            raise e
    

def leave_meeting():
    browser.execute_script("document.getElementById('roster-button').click()")
    while get_current_participants() > MINIMUM_PARTICIPANTS:
        sleep(60)
    print_message('Leaving', status_code.LOADING)
    browser.execute_script("document.getElementById('hangup-button').click()")
    print_message('Left Meeting at {}'.format(datetime.now()) , status_code.SUCCESS)


          
