from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import os

def set_options(): 
    options = Options()
    options.add_argument("--disable-infobars")
    options.add_argument("start-maximized")
    options.add_argument("--disable-extensions")
    
    # Advanced Stealth Flags
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36")
    options.add_argument("--disable-notifications")
    options.add_argument("--lang=en-US")
    options.add_argument("--remote-allow-origins=*")
    options.add_argument("--disable-features=ExternalProtocolDialog")
    options.add_argument("--disable-external-intent-requests")
    
    # Use a dedicated Chrome profile for the bot to avoid conflicts
    # This creates a folder named 'chrome_profile' in your project directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    user_data_path = os.path.join(script_dir, "chrome_profile")
    options.add_argument(f"user-data-dir={user_data_path}")
    options.add_argument("profile-directory=Default")
    
    # Pass the argument 1 to allow and 2 to block
    options.add_experimental_option("prefs", {
        "profile.default_content_setting_values.media_stream_mic": 1,
        "profile.default_content_setting_values.media_stream_camera": 1,
        "profile.default_content_setting_values.notifications": 1,
        "protocol_handler.excluded_schemes.msteams": True # BLOCK the app auto-opening
    })
    return options


def get_driver():
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=set_options())



