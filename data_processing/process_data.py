"""
Generate dependent variables and features from raw stock information

Input:
    data/stock_dict.pickle

Output:
    data/stock_price.csv
    
"""


import pickle
from tqdm import tqdm
import os

basic_folder = os.getcwd()
basic_folder = basic_folder.split("\\")
basic_folder = "/".join(basic_folder[:3]+['OneDrive','stock_analysis'])
os.chdir(basic_folder)

from data_processing.generate_variables import (get_ta_lib_indicator, 
                             add_ts_indicators, 
                             priceChangeForward,
                             get_ext_indicator)


# In[Generate dependent variables and features]
class ProcessStockData():
    def dic_to_df():
        with open('data/stock_dict.pickle', 'rb') as f:
            stock_dic = pickle.load(f)

        # startTime = time.time()

        DAYS_PRED = 5
        for count, stock in enumerate(tqdm(stock_dic)):
            
            df = stock_dic[stock].copy()
            df = get_ta_lib_indicator(df)  
            df = add_ts_indicators(df)
            df = priceChangeForward(df, DAYS_PRED, 'close')      
            
            if count == 0:
                stocks_df = df
            else:
                stocks_df = stocks_df.append(df)
        
        # executionTime = (time.time() - startTime)
        # print('Execution time in seconds:', executionTime)
        
        stocks_df = get_ext_indicator(stocks_df)
        
        # print(max(stocks_df["datetime"]))
        
        stocks_df.to_csv("data/stock_price.csv")