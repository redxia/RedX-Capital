from utilities import utilities
if not utilities.business_day():
    sys.exit()
from datetime import datetime
import pandas as pd
from selenium import webdriver # Use Chrome Browser
import time
from selenium.webdriver.common.by import By
import sys
import pandas.io.formats.excel
pandas.io.formats.excel.ExcelFormatter.header_style=None
url=r"https://www.barchart.com/etfs-funds/quotes/SPY/put-call-ratios"

options=webdriver.ChromeOptions()
# options.headless=True
options.add_argument('start-maximized')
driver=webdriver.Chrome(options=options)
driver.get(url)

time.sleep(10)
scraped_tables=driver.find_elements(By.XPATH, '//*[@id="main-content-column"]/div/div[3]/div')[0].text
scraped_tables=scraped_tables.split('\n')
df=pd.DataFrame(columns=scraped_tables[:9])
for i in range(1,int((len(scraped_tables))/9)):
    df.loc[i-1]=scraped_tables[i*9:(i+1)*9]

date=datetime.now().strftime("%Y%m%d")
df.to_csv(r"C:\RedXCapital\Dividends\Data\SPY PUT CALL RATIO\SPY_PCALLRATIO_"+date+".csv", index=0)
driver.quit()