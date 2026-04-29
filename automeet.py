from resources import *
from actions import *


#Login
browser.get(TEAMS_CALENDAR_URL)
wait_for_login()

#Join Meeting
if MEETING_LINK:
    join_via_link(MEETING_LINK)
else:
    print_message('Looking for a meeting to join on the calendar', status_code.LOADING)
    keep_finding(JOIN_BUTTON, 60).click()
    sleep(5)
    join_meeting()

# --- START AUDIENCE MONITORING (VOSK) ---
from audio_processor import start_processor_background
processor = start_processor_background()

#Keep track of participants and leave
leave_meeting()

# --- STOP MONITORING AND SAVE TRANSCRIPT ---
processor.stop()
processor.save_transcript()




    




