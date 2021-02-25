

import pandas as pd
#import rpy2.robjects as robjects
#from rpy2.robjects import pandas2ri
from datetime import date, timedelta, datetime
import sys
import os
#sys.path.append("/Users/apple/Desktop/dash/doge_plus/scripts")  # setwd to load my scripts


main_path = os.path.dirname(os.path.abspath(__file__)) + '/'
reddit_file_name = str(sys.argv[2])


crypto_names_file_name = main_path + "raw_data/crypto_names.csv"
df = pd.read_csv(crypto_names_file_name)


# get today's info
reddit = pd.read_csv(reddit_file_name)
today_data = df.merge(reddit, left_on ='symbol', right_on ='symbol')
today = str(date.today())
today_data['Date'] = today


# update last 30 days, or create new file if starting from scratch
data_for_app_filename = main_path + "raw_data/data_for_app.csv"
if os.path.exists(data_for_app_filename):
  main = pd.read_csv(data_for_app_filename)
  main = main.append(today_data)
  
  # as precaution, removing any non unique date/symbol combinations
  main = main.drop_duplicates(subset=['symbol', 'Date'])
  
  # drop things over a month old
  today = date.today()
  cutoff_date = today - timedelta(30)
  #datetime.strptime(main['Date'][1], "%Y-%m-%d").date()
  dates = pd.to_datetime(main['Date'])
  ix = dates > pd.to_datetime(cutoff_date)
  main = main.loc[ix]
  main.to_csv(data_for_app_filename, index = False)
  
else:
  today_data.to_csv(data_for_app_filename, index = False)

 
