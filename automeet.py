from resources import *
from actions import *
from time import sleep

#Login
browser.get(TEAMS_CALENDAR_URL)
wait_for_login()

processor = None

while True:
    try:
        #Join Meeting
        if MEETING_LINK:
            join_via_link(MEETING_LINK)
        else:
            print_message('Looking for a meeting to join on the calendar', status_code.LOADING)
            keep_finding(JOIN_BUTTON, 60).click()
            sleep(5)
            join_meeting()

        # --- START AUDIENCE MONITORING ---
        from audio_processor import start_processor_background
        processor = start_processor_background()

        #Keep track of participants and leave
        leave_meeting()
        
        # If we reach here, it means we left the meeting normally (participant count dropped)
        print_message("Meeting ended normally.", status_code.SUCCESS)
        break

    except Exception as e:
        print_message(f"An error occurred: {e}", status_code.FAILED)
        print_message("Attempting to rejoin in 30 seconds...", status_code.LOADING)
        if processor:
            processor.stop()
        sleep(30)

# --- STOP MONITORING AND SAVE TRANSCRIPT ---
if processor:
    processor.stop()
    processor.save_transcript()
