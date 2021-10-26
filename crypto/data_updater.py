import pandas as pd
from utilities import util
%load_ext autoreload
%autoreload 2

crypto_master=pd.read_csv("D:\RedX Capital\crypto\crypto_master.csv")

for idx, value in enumerate(crypto_master['download_url']):
  print('Downloading Ticker: ', crypto_master.loc[idx, 'NAME'], ',', crypto_master.loc[idx, 'TICKER'])
  util.download_data(value)

print("Completed Downloading")

updated_data_dir=r"D:\RedX Capital\crypto\Data\master_data\temp"
updated_data_files=util.get_names_directory(updated_data_dir)

master_data_dir=r"D:\RedX Capital\crypto\Data\master_data"
master_data_files=util.get_names_directory(master_data_dir)

util.update_data(master_data_files, updated_data_files)
print("Completed added new data")


import os
for i in updated_data_files:
  os.remove(i)
  print("Removing file: ", i)