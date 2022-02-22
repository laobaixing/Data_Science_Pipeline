"""
Generate dependent variables and features from raw stock information

Input:
    data/stock_dict.pickle

Output:
    data/stock_price.csv
    
"""


import pickle
from tqdm import tqdm

from data_processing.generate_variables import (get_ta_lib_indicator, 
                             add_ts_indicators, 
                             priceChangeForward,
                             get_ext_indicator)


# In[Generate dependent variables and features]
class ProcessStockData():
    def dic_to_df(self, input_data_file, output_data_file):
        with open(input_data_file, 'rb') as f:
            stock_dic = pickle.load(f)

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
               
        stocks_df = get_ext_indicator(stocks_df)        
        
        stocks_df.to_csv(output_data_file, index = False)