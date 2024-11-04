from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.firefox.options import Options as FirefoxOptions
import requests


class WebScarpingToolInit:
    def initialize_driver(self,driver="firefox"):
        if driver.lower()=="firefox":
            options = FirefoxOptions()
            options.add_argument("--headless")
            options.add_argument('--no-proxy-server')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('log-level=3')
            driver = webdriver.Firefox(options=options)
            return driver
        
        else:
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument("window-size=1100,641")
            prefs = {'profile.default_content_setting_values': {'cookies': 2, 'images': 2, 
                            'plugins': 2, 'popups': 2, 'geolocation': 2, 
                            'notifications': 2, 'auto_select_certificate': 2, 'fullscreen': 2, 
                            'mouselock': 2, 'mixed_script': 2, 'media_stream': 2, 
                            'media_stream_mic': 2, 'media_stream_camera': 2, 'protocol_handlers': 2, 
                            'ppapi_broker': 2, 'automatic_downloads': 2, 'midi_sysex': 2, 
                            'push_messaging': 2, 'ssl_cert_decisions': 2, 'metro_switch_to_desktop': 2, 
                            'protected_media_identifier': 2, 'app_banner': 2, 'site_engagement': 2, 
                            'durable_storage': 2}}
            chrome_options.add_experimental_option('prefs', prefs)
            chrome_options.add_argument('--no-proxy-server')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument('log-level=3')
            driver = webdriver.Chrome(options=chrome_options)
            return driver
    
    def initialize_requests_client(self,link=None)->requests.Response:

        if link is None:
            raise ValueError("Please Provide an appropriate link")
    
        try:
            page=requests.get(link)
            return page
        
        except Exception as e:
            raise Exception("Error in requesting entered link,"+
                            "please check your input and connection")
