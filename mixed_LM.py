# -*- coding: utf-8 -*-
"""
Build the model through Mixed linear

Input:
    data/stock_price.csv
    
Output:
    

Created on Sat Nov 27 10:43:58 2021

@author: Ling
"""

import pandas as pd
import numpy as np
import statsmodels.api as sm
# import multiprocessing as mp

from datetime import datetime
import os

basic_folder = os.getcwd()
basic_folder = basic_folder.split("\\")
basic_folder = "/".join(basic_folder[:3]+['OneDrive','Time_Series'])
os.chdir(basic_folder)

stocks_df = pd.read_csv("data/stock_price.csv")

# In[Model training]
df_train = stocks_df[(stocks_df['datetime'] < 
                      datetime.strptime('2020-12-31', "%Y-%m-%d").date())]
df_val = stocks_df[(stocks_df['datetime'] >= 
                    datetime.strptime('2020-12-31', "%Y-%m-%d").date())]


# use its own normalized base line to represent recent emotion.
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

print(mlm_result.summary())

# get the random effects coefs
mlm_result.random_effects

val_predict = mlm_result.predict(df_val)
y_val = np.array(df_val['price_change_forward_ratio'])
# error_val = mean_squared_error(y_val, np.array(val_predict))

# print(sqrt(error_val))

# use the rank order metrics
print("The correlation between the pridction and actual price change ratio \
      in training set")
print(np.corrcoef(tra_predict, y_tra))  # also much lower


x = pd.DataFrame({'predict':val_predict, 'real':y_val, 'symbol': df_val['symbol']})
x['predict_cuts'] = pd.qcut(x['predict'], [0, 0.05, .15, .5, .85, .95,  1.]                            
                            , labels=['low','medium_1', 'medium-2', 'medium-3','medium-4','high'])
print("the relationship between gain of the predicted risk level and real risk level")
print(x.groupby(['predict_cuts']).agg('mean'))

df_val['predict'] = val_predict
df_val['predict_cuts'] = x['predict_cuts']

# get the last item of a group, check other methods
for count, stock in enumerate(stocks):
    y = x[x['symbol']==stock]
    if count ==0:
        last_day_stocks = y.tail(1)
    else:
        last_day_stocks = last_day_stocks.append(y.tail(1))

print("list the prediction of stock")
print(last_day_stocks[['symbol','predict', 'predict_cuts', 'real']].sort_values(by=['predict'],ascending=False))
