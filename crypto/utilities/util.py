def download_data(str_url):
    import undetected_chromedriver as uc
    from selenium import webdriver
    import time
    option = webdriver.ChromeOptions()
    option.add_argument("start-maximized")
    option.add_argument("--disable-blink-features=AutomationControlled")
    option.add_argument("--disable-blink-features")
    prefs={"download.default_directory" : r"D:\RedXCapital\crypto\Data\master_data\temp"}
    option.add_experimental_option("prefs", prefs)
    driver=uc.Chrome(options=option)
    driver.implicitly_wait(2)
    driver.get(str_url)
    time.sleep(3.5)
    driver.quit()
    return


def get_names_directory(root_dir): # returns a list for all the files within a directory
    import os
    from fnmatch import fnmatch # grabs only csv
    pattern = "*.csv"
    file_names=[]
    for path, subdirs, files in os.walk(root_dir):
        if "temp" in subdirs:
            subdirs.remove("temp")
        for name in files:
            if fnmatch(name, pattern):
                file_names.append(os.path.join(path, name))
    return file_names

def update_data(master_files_list, update_files_list):
    import pandas as pd
    master_data_names=[k.split("\\")[-1] for k in master_files_list]

    for i in update_files_list:
        update_df=pd.read_csv(i)
        recent_5_days=update_df.tail(10).copy()
        recent_5_days_dates=pd.to_datetime(recent_5_days['snapped_at']).dt.date

        if i.split("\\")[-1] in master_data_names: # checking if the update file is in master file
            idx_master=master_data_names.index(i.split("\\")[-1]) # grabs the index for the master file name
            master_df=pd.read_csv(master_files_list[idx_master])# if true then proceed to update the master_data
            master_df=master_df[:-1] # remove the last row because download usually dynamically download this data
            master_df_dates=pd.to_datetime(master_df['snapped_at']).dt.date
            print("Updating file: ", master_files_list[idx_master])
            for idx, value in enumerate(recent_5_days_dates): # updating the master df
                if sum(value == master_df_dates) < 1:
                    master_df=master_df.append(recent_5_days.iloc[idx])
                    print('Added new data.')
            master_df.to_csv(master_files_list[idx_master], index=False)
    return
# TODO only update today if it pasts the UTC time 
# TODO delete the temp file
# from datetime import datetime
# datetime.utcnow() > datetime.utcnow().replace(hour=0,minute=0,second=0, microsecond=0