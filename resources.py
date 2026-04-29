import toml
import enum
from driver_factory import get_driver


#Important determinations and constants
browser = get_driver()  
TEAMS_CALENDAR_URL = 'https://teams.microsoft.com/v2/' 

#XPaths
JOIN_BUTTON = '//button[@title="Join"]'
EMAIL_FIELD = '//*[@id="i0116"]'
NEXT_BUTTON = '//*[@id="idSIButton9"]'
PASSWORD_FIELD = '//input[@type="password" or @id="i0118"]'
STAY_SIGNED_IN_BUTTON = '//*[@id="idSIButton9"]'
NEW_MEETING_BUTTON = '//button[contains(@id, "new_meeting") or contains(text(), "meeting") or @title="Chat" or @title="Meet"]'
CAMERA_BUTTON = '//*[contains(@title, "camera") or contains(@aria-label, "camera")]'
MIC_BUTTON = '//*[contains(@title, "microphone") or contains(@aria-label, "microphone") or contains(@title, "mic")]'
PREJOIN_JOIN_BUTTON = '//button[contains(@data-tid, "prejoin-join-button") or contains(text(), "Join now") or contains(text(), "Join Now") or contains(text(), "Join meeting")]'
OOPS = '//*[@class=oops]'
TRY_AGAIN_BUTTON = '//button[@translate-once="tryAgain"]'
PARTICIPANTS_BUTTON = '//button[@id="roster-button"]'
USE_TEAMS_ON_WEB_BUTTON = '//button[contains(text(), "Use Teams on the web") or contains(text(), "Continue on this browser")]'
GUEST_NAME_FIELD = '//input[contains(@placeholder, "name") or contains(@aria-label, "name") or contains(@id, "username") or @type="text"]'
CURRENTLY_IN_MEETING = '//*[@id="page-content-wrapper"]/div[1]/div/calling-screen/div/div[2]/meeting-panel-components/calling-roster/div/div[4]/div/div[1]/accordion/div/accordion-section[2]/div/calling-roster-section/div/div[1]/button/span[3]'
# Generic Leave/Hangup buttons for any Teams variant
HANGUP_BUTTON = '//button[contains(@id, "hangup") or contains(@aria-label, "Leave") or contains(@aria-label, "leave") or contains(@title, "Leave") or contains(@id, "leave") or contains(@data-tid, "hangup")]'


#Messages
OOPS_MESSAGE = 'Something went wrong. Please run the script again'
LOGIN_SUCCESSFUL = 'Login Successful!'
LOGIN_FAILED = 'Oops! Login Failed.'
CONNECTION_TIMEOUT = """Connection took too much time. Script may still work, its just wasn't able too verify the connection because it took long to respond.
                        Here's what you can do, if it doesn't work:
                            1. Try running the script again. If your internet works slightly faster this time, this should work.
                            2. If the above solution doesn't work. Try increasing timeout in advanced settings and run the script again."""

#Status for messages
class status_code(enum.Enum):
    SUCCESS = 1
    LOADING = 2
    FAILED = 3 


#Data from Settings
data = toml.load(open('settings.toml'))

EMAIL_ID = data['email_id']
PASSWORD = data['password']
MEETING_LINK = data.get('meeting_link', '')
MINIMUM_PARTICIPANTS = data['minimum_participants']
TIMEOUT = data['timeout']
