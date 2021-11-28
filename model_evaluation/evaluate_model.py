# -*- coding: utf-8 -*-
"""
Evaluate the model result for stocks

Input:
    data/mixed_lm_val_pred.csv
    data/mixed_lm_tra_pred.csv
Output:
    output/stock_model_evaluation.xlsx

Created on Sat Nov 27 17:55:55 2021

@author: Ling
"""

import pandas as pd
import numpy as np
import os
from sklearn.metrics import mean_squared_error
from matplotlib import pyplot as plt

basic_folder = os.getcwd()
basic_folder = basic_folder.split("\\")
basic_folder = "/".join(basic_folder[:3]+['OneDrive','stock_analysis'])
os.chdir(basic_folder)

val_predict = pd.read_csv("data/mixed_lm_val_pred.csv")
tra_predict = pd.read_csv("data/mixed_lm_tra_pred.csv")

# In[RMSE]

val_rmse = round(mean_squared_error(val_predict['prediction'], 
                               val_predict.price_change_forward_ratio,
                               squared = False), 4)
tra_rmse = round(mean_squared_error(tra_predict['prediction'], 
                               tra_predict.price_change_forward_ratio,
                               squared = False),4)

val_mean_rmse = round(mean_squared_error(
    [val_predict.price_change_forward_ratio.mean()]*val_predict.shape[0], 
                               val_predict.price_change_forward_ratio,
                               squared = False), 4)
tra_mean_rmse = round(mean_squared_error(
    [tra_predict.price_change_forward_ratio.mean()]*tra_predict.shape[0], 
                               tra_predict.price_change_forward_ratio,
                               squared = False),4)

rmse_tb = pd.DataFrame({'dataset':["train", "validation"],
                        'rmse':[tra_rmse, val_rmse],
                        'pred_mean':[tra_predict['prediction'].mean(),
                                     val_predict['prediction'].mean()],
                        'pred_std':[tra_predict['prediction'].std(),
                                     val_predict['prediction'].std()],
                        'price_change_ratio_mean':
                            [tra_predict['price_change_forward_ratio'].mean(),
                             val_predict['price_change_forward_ratio'].mean()],
                        'price_change_ratio_std':
                            [tra_predict['price_change_forward_ratio'].std(),
                             val_predict['price_change_forward_ratio'].std()]})

print(rmse_tb)

# In[Correlation between the prediction and the price change ratio]
val_cor = np.corrcoef(val_predict['prediction'], 
                  val_predict['price_change_forward_ratio'])
tra_cor = np.corrcoef(tra_predict['prediction'], 
                  tra_predict['price_change_forward_ratio'])

cor_tb = pd.DataFrame({'dataset':["train", "validation"],
                        'cor_pred_ori':[tra_cor[0,1], val_cor[0,1]]})
                        

# In[Output to the excel]
with pd.ExcelWriter('output/stock_model_evaluation.xlsx') as writer:  
    rmse_tb.to_excel(writer, sheet_name='RMSE', index=True)
    
with pd.ExcelWriter('output/stock_model_evaluation.xlsx', mode="a") as writer:  
    cor_tb.to_excel(writer, sheet_name='Cor_pred_ori_depend', index=True)

# In[Residual plots]
fig = plt.figure()
plt.scatter(val_predict['price_change_forward_ratio'], 
                val_predict['prediction'])

val_resid = val_predict['price_change_forward_ratio'] - val_predict['prediction']
fig = plt.figure()
plt.scatter(val_predict['price_change_forward_ratio'], 
                val_resid)

tra_resid =tra_predict['price_change_forward_ratio'] - tra_predict['prediction'] 
fig = plt.figure()
plt.scatter(tra_predict['price_change_forward_ratio'], 
                tra_resid)



