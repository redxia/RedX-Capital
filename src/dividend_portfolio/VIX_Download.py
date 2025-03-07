import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time
from utilities import utilities

download_path=os.getcwd()+r'\Data\Vix3mo'
# Configure Chrome options for headless browsing
chrome_options = Options()
#chrome_options.add_argument("--headless")
#chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--start-fullscreen")
chrome_options.add_experimental_option("prefs", {
    "download.default_directory": download_path,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "plugins.always_open_pdf_externally": True
})

# Initialize the webdriver
driver = webdriver.Chrome(executable_path=os.getcwd()+'\chromedriver.exe', options=chrome_options)

# Go to the URL
url = "https://www.cboe.com/us/indices/dashboard/vix3m/"
driver.get(url)

# Locate the download button using its class name
wait = WebDriverWait(driver, 10)

element = wait.until(EC.element_to_be_clickable(driver.execute_script('return document.querySelector("#hist-chart > span");')))
time.sleep(2)
element.click()
time.sleep(5)
download_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[download="vix3m-history.csv"]')))
time.sleep(2)
# Click the download button
download_button.click()
time.sleep(10)

# Close the browser
driver.quit()

today=utilities.last_business(utilities.next_business()).strftime("%Y%m%d")
os.rename(r"C:\RedXCapital\Dividends\Data\Vix3mo\vix3m-history.csv",r"C:\RedXCapital\Dividends\Data\Vix3mo\vix3m-history_"+today+'.csv')