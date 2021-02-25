

import pandas as pd
from datetime import date, timedelta, datetime
import sys
import os
from get_crypto_prices import get_crypto_prices


output_path =  main_path = str(sys.argv[1])  # taking output file from terminal 


# get df crypto prices
df = get_crypto_prices()
crypto_names_file_name = output_path + "raw_data/crypto_names.csv"
print('saving crypto names to:', crypto_names_file_name)
df.to_csv(crypto_names_file_name, index = False)














