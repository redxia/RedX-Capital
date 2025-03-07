from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from bs4 import BeautifulSoup
import os
from datetime import datetime
from slack_sdk import WebClient
from datetime import datetime
from slack_sdk.webhook import WebhookClient
import time
from webdriver_manager.chrome import ChromeDriverManager
# from datetime import timedelta

url=r"https://hooks.slack.com/services/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" #ara team
webhook=WebhookClient(url)
token="xoxb-5807389180627-5804703738981-ovb9XJnGAyncpU8GV89OXkMn"
client=WebClient(token)

chrome_options = Options()
# chrome_options.headless=True
chrome_options.add_argument("start-maximized")
chrome_options.add_experimental_option("prefs", {
    "download.default_directory": os.getcwd(),
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "plugins.always_open_pdf_externally": True
})

start_time=datetime.now()
try:
    driver = webdriver.Chrome(executable_path=os.getcwd()+'\chromedriver.exe', options=chrome_options)
except:
    installation=ChromeDriverManager().install()
    os.replace(installation, "chromedriver.exe")
    
driver.get(r'https://finviz.com/calendar.ashx')
time.sleep(1.5)
soup = BeautifulSoup(driver.page_source, 'html.parser')
tables = soup.find_all('table')
table=tables[(start_time.weekday()+5)]
td_table=[]
td_tags = table.find_all('tr')
for td in td_tags:
        td_table.append(td.get_text().replace('\n',' | '))

for i in td_table[1:]:
    time_now=datetime.now()
    get_morning_eve=i.split('|')[1].strip().split(':')[1].split(' ')[1]
    hour=int(i.split('|')[1].strip().split(':')[0])
    hour_adj=hour+12 if get_morning_eve=='PM' else hour
    minute=int(i.split('|')[1].strip().split(':')[1].split(' ')[0])
    time_now=time_now.replace(hour=hour_adj, minute=minute,second=0,microsecond=0)
    try:
        response = client.chat_scheduleMessage(
        channel="C05Q43MPGRF",
        text="<!here> Date: "+time_now.strftime("%m/%d/%Y")+". Economic News! "+i,
        post_at=int(time_now.timestamp()))
    except:
        webhook.send(text="Failed to send: "+i)
        
        
# def finviz_calendar(driver):
# driver.get(r'https://finviz.com/calendar.ashx')
# soup = BeautifulSoup(driver.page_source, 'html.parser')
# tables = soup.find_all('table')
# table=tables[(start_time.weekday()+5)]
webhook.send(text='Date: '+start_time.strftime("%m/%d/%Y")+". Link: "+driver.current_url+" \n"+ "Today's Economic News")
# td_table=[]
# td_tags = table.find_all('tr')
# for td in td_tags:
#         td_table.append(td.get_text().replace('\n',' | '))    
for i in td_table:
    webhook.send(text=i+'\n')
    # return driver

webhook.send(text="-"*10)    
# finviz_calendar(driver)