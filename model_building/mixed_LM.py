"""
Build the model through Mixed linear

Input:
    data/stock_price.csv
    
Output:
    data/mixed_lm_val_pred.csv
    data/mixed_lm_tra_pred.csv	

"""

import pandas as pd
import statsmodels.api as sm

from datetime import datetime


class MixedLM():
    def mixed_lm(self, input_data_file):
        stocks_df = pd.read_csv(input_data_file)
        
        # In[Model training]
        stocks_df['datetime'] = pd.to_datetime(stocks_df['datetime']).dt.date
        
        df_train = stocks_df[(stocks_df['datetime'] < 
                              datetime.strptime('2021-3-31', "%Y-%m-%d").date())]
        df_val = stocks_df[(stocks_df['datetime'] >= 
                            datetime.strptime('2021-3-31', "%Y-%m-%d").date())]
        
        # Normalize RSI
        df_train['RSI_cen'] = df_train.groupby('symbol').RSI.transform(lambda x: x - x.mean())
        df_val['RSI_cen'] = df_val.groupby('symbol').RSI.transform(lambda x: x - x.mean())
        
        features = ['average_13_60_down',"RSI_cen" ] #"MACD", 
        
        df_train = df_train.dropna(subset = ['price_change_forward_ratio'] + features )
        df_val = df_val.dropna(subset = ['price_change_forward_ratio'] + features )
        
        df_train = df_train.loc[~df_train.symbol.isin(["BB", "QS", "AI", "MAXR", "PLTR"])]
        df_val = df_val[~df_val.symbol.isin(["BB", "QS", "AI", "MAXR", "PLTR"])]
        
        # This model is only on the slope
        formula = 'price_change_forward_ratio ~' + "+".join(features)
        mlm_mod = sm.MixedLM.from_formula(
            formula = formula, 
            groups = 'symbol', 
            re_formula = "~RSI_ind + SAR_diff_ind",
            data = df_train
        )
        
        # Run the fit
        mlm_result = mlm_mod.fit(method=["lbfgs"])
        
        # In[Output the model result and prediction]
        val_predict = pd.DataFrame({'prediction':mlm_result.predict(df_val)})
        val_predict = pd.concat([df_val[['datetime', 'price_change_forward_ratio']], 
                                       val_predict], axis = 1)
        
        tra_predict = pd.DataFrame({'prediction':mlm_result.predict(df_train)})
        tra_predict = pd.concat([df_train[['datetime', 'price_change_forward_ratio']], 
                                       tra_predict], axis = 1)
        
        val_predict.to_csv("data/mixed_lm_val_pred.csv")
        tra_predict.to_csv("data/mixed_lm_tra_pred.csv")


