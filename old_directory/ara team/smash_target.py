# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from slack_sdk.webhook import WebhookClient
# from selenium import webdriver
# import os
# from datetime import datetime
# import time
# import yfinance as yf
# from bs4 import BeautifulSoup
# import polygon
# client=polygon.RESTClient(os.environ.get('polygon_api'))
# url=r"https://hooks.slack.com/services/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"
# webhook=WebhookClient(url)

# chrome_options = Options()
# #chrome_options.add_argument("--headless")
# chrome_options.add_argument("start-maximized")
# chrome_options.add_experimental_option("prefs", {
#     "download.default_directory": os.getcwd(),
#     "download.prompt_for_download": False,
#     "download.directory_upgrade": True,
#     "plugins.always_open_pdf_externally": True
# })

# start_time=datetime.now()

# driver = webdriver.Chrome(executable_path=os.getcwd()+'\chromedriver.exe', options=chrome_options)
# time.sleep(1)
# driver.get(r"https://newsletter.smashelito.com/")
# time.sleep(3)
# try:
#     driver.find_elements(By.XPATH, r'//*[@id="main"]/div[2]/div[3]/div/div/div[1]/a/button')[0].click() # clicks on no subscription
# except:
#     pass

# time.sleep(2.5)
# # driver.find_elements(By.XPATH, r'//*[@id="home-body"]/div[1]/div/div[1]/div[2]/div[1]/div/div[1]')[0].click() # clicks on the first articles

# driver.find_elements(By.XPATH, r'//*[@id="main"]/div[2]/div[1]/div[1]/div/div/div')[0].click() # clicks on the first articles


# introduction='Date: '+start_time.strftime("%m/%d/%Y")+". Link: "+driver.current_url+" \n"
# spx = round(yf.Ticker('^GSPC').history()['Close'][-1],2)

# def weekly_plan(driver):
#     #daily_text
#     daily_text=driver.find_elements(By.XPATH,r'//*[@id="main"]/div[2]/div/div[1]/div/article/div[4]/div[1]/div/p[1]/span[1]')[0].text
#     weekly_text=driver.find_elements(By.XPATH,r'//*[@id="main"]/div[2]/div/div[1]/div/article/div[4]/div[1]/div/p[1]/span[2]')[0].text+'  *Weekly*'+driver.find_elements(By.XPATH,r'//*[@id="main"]/div[2]/div/div[1]/div/article/div[4]/div[1]/div/p[1]/span[3]')[0].text
#     monthly_text=driver.find_elements(By.XPATH,r'//*[@id="main"]/div[2]/div/div[1]/div/article/div[4]/div[1]/div/p[1]/span[4]')[0].text+'  *Monthly*'+driver.find_elements(By.XPATH,r'//*[@id="main"]/div[2]/div/div[1]/div/article/div[4]/div[1]/div/p[1]/span[5]')[0].text

#     weekly_extreme_high='*Weekly Extreme High* '+driver.find_element(By.XPATH,r'//*[@id="main"]/div[2]/div/div[1]/div/article/div[4]/div[1]/div/p[2]/span[1]').text

#     weekly_extreme_low='*Weekly Extreme Low* '+driver.find_element(By.XPATH,r'//*[@id="main"]/div[2]/div/div[1]/div/article/div[4]/div[1]/div/p[2]/span[2]').text

#     upside=driver.find_element(By.XPATH,r'//*[@id="main"]/div[2]/div/div[1]/div/article/div[4]/div[1]/div/p[8]/span[1]').text+' *Upside:* '+driver.find_element(By.XPATH,r'//*[@id="main"]/div[2]/div/div[1]/div/article/div[4]/div[1]/div/p[8]/strong[2]').text+driver.find_element(By.XPATH,r'//*[@id="main"]/div[2]/div/div[1]/div/article/div[4]/div[1]/div/p[8]/span[3]').text

#     downside=driver.find_element(By.XPATH,r'//*[@id="main"]/div[2]/div/div[1]/div/article/div[4]/div[1]/div/p[8]/span[4]').text+' *Downside:* '+driver.find_element(By.XPATH,r'//*[@id="main"]/div[2]/div/div[1]/div/article/div[4]/div[1]/div/p[8]/strong[4]').text+driver.find_element(By.XPATH,r'//*[@id="main"]/div[2]/div/div[1]/div/article/div[4]/div[1]/div/p[8]/span[6]').text

#     webhook.send(text=introduction+'*SPX Index:* '+str(round(spx,2))+'\n'+daily_text+"\n"+weekly_text+'\n'+monthly_text+'\n'+weekly_extreme_high+'\n'+weekly_extreme_low+'\n'+upside+'\n'+downside)
#     return driver

# def daily_plan(driver):
#     observe=driver.find_element(By.XPATH,r'//*[@id="main"]/div[2]/div/div[1]/div/article/div[4]/div[1]/div/p[6]').text
#     try:
#         observe1=driver.find_element(By.XPATH,r'//*[@id="main"]/div[2]/div/div[1]/div/article/div[4]/div[1]/div/p[7]').text
#     except:
#         pass
#     first_bullet=driver.find_element(By.XPATH,r'//*[@id="main"]/div[2]/div/div[1]/div/article/div[4]/div[1]/div/ul[1]/li[1]/p').text
#     second_bullet=driver.find_element(By.XPATH,r'//*[@id="main"]/div[2]/div/div[1]/div/article/div[4]/div[1]/div/ul[1]/li[2]/p').text
#     third_bullet=driver.find_element(By.XPATH,r'//*[@id="main"]/div[2]/div/div[1]/div/article/div[4]/div[1]/div/ul[2]/li[1]/p').text
#     fourth_bullet=driver.find_element(By.XPATH,r'//*[@id="main"]/div[2]/div/div[1]/div/article/div[4]/div[1]/div/ul[2]/li[2]/p').text
    
#     try:
#         webhook.send(text=introduction+'*SPX Index:* '+str(round(spx,2))+'\n'+observe+"\n"+observe1+'\n'+first_bullet+'\n'+second_bullet+'\n'+third_bullet+'\n'+fourth_bullet+'\n')
#     except:
#         webhook.send(text=introduction+'*SPX Index:* '+str(round(spx,2))+'\n'+observe+"\n"+first_bullet+'\n'+second_bullet+'\n'+third_bullet+'\n'+fourth_bullet+'\n')
#     return driver

# def finviz_calendar(driver):
#     driver.get(r'https://finviz.com/calendar.ashx')
#     soup = BeautifulSoup(driver.page_source, 'html.parser')
#     tables = soup.find_all('table')
#     table=tables[(start_time.weekday()+6)]
#     webhook.send(text='Date: '+start_time.strftime("%m/%d/%Y")+". Link: "+driver.current_url+" \n"+ "Tomrrow's Economic News")
#     td_table=[]
#     td_tags = table.find_all('tr')
#     for td in td_tags:
#             td_table.append(td.get_text().replace('\n',' | '))    
#     for i in td_table:
#         webhook.send(text=i+'\n')
#     return driver

# # if start_time.weekday()>=4:
# #     driver=weekly_plan(driver)
# # else:
# #     driver=daily_plan(driver)
# # webhook.send(text="-"*10)    
# # finviz_calendar(driver)

# # driver.quit()



# # //*[@id="main"]/div[2]/div/div[1]/div/article/div[4]/div[1]/div/div[8]/figure/a/div/picture/img