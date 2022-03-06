"""
Build the model through XGBoost

Input:
    data/stock_price.csv
    
Output:
    data/xgboost_val_pred.csv
    data/xgboost_tra_pred.csv	

"""

from matplotlib import pyplot as plt
import pandas as pd
import numpy as np
from datetime import datetime
import xgboost as xgb
from sklearn.model_selection import RandomizedSearchCV
from sklearn.inspection import plot_partial_dependence
import shap


class XGBoostStock():
    def xgboost_stock(self, input_data_file):
        stocks_df = pd.read_csv(input_data_file)

        one_hot = pd.get_dummies(stocks_df[['MACD_ind', "RSI_ind", 'mfi_ind', "symbol"]], 
                                 drop_first=True)
        stocks_df = stocks_df.join(one_hot)
        
        stocks_df["datetime"] = pd.to_datetime(stocks_df['datetime']).dt.date
        
        df_train = stocks_df[(stocks_df['datetime'] < 
                              datetime.strptime('2021-3-31', "%Y-%m-%d").date())]
        df_val = stocks_df[(stocks_df['datetime'] >= 
                            datetime.strptime('2021-3-31', "%Y-%m-%d").date())]
        
        # #### XGBoost
        # - One hot encode
        # - Split to train and validation, then go to XGBoost matrix
        # - Output the variable importance
        # - Plot partial dependence
        # - SHAP
        
        features = ['ma13', 'ma60', 'ma200', 'RSI', 'MACD', 'MACD_ewm9', 'MACD_diff', 
                    'average_13_60_down', 
                    "MACD_ind_MACD_2", "MACD_ind_MACD_3", "MACD_ind_MACD_4", 
                    "RSI_ind_RSI_2", "RSI_ind_RSI_3", "RSI_ind_RSI_4", 
                    'ad','SAR_diff', 'mfi', 'upperband','lowerband', 'ma13_diff_ratio', 
                    'ma60_diff_ratio', 'ma200_diff_ratio','B_upper_band_diff',
                    'B_lower_band_diff'] 
                
        df_train = df_train.dropna(subset = ['price_change_forward_ratio'] + features )
        df_val = df_val.dropna(subset = ['price_change_forward_ratio'] + features )
              
        X_train = np.array(df_train[features])
        y_train = np.array(df_train['price_change_forward_ratio'])
        
        X_val = np.array(df_val[features])
        y_val = np.array(df_val['price_change_forward_ratio'])
        
        parameters = {'objective':['reg:squarederror'],
                      'booster':['gbtree'], 
                      # general parameters
                      'learning_rate': [0.05,0.2], 
                      "reg_alpha"   : [0.2,2],
                      "reg_lambda"  : [1,3],
                      'n_estimators': [50, 200],
                      # Tree parameters
                      'max_depth': [3,7],
                      'min_child_weight': [10,20],
                      # sampling
                      'subsample': [0.8],
                      'colsample_bytree': [0.7, 0.9],
                      # "gamma"       : [0, 0.2]
                      }
        
        # Use sklearn wrapper
        xgbr = xgb.XGBRegressor(random_state=30,  verbosity =1)
        
        grid_obj_xgb = RandomizedSearchCV(xgbr, parameters, cv=3,n_iter= 10,
                                          scoring='neg_mean_squared_error',verbose=2, 
                                          random_state=10,n_jobs=4)
        
        grid_obj_xgb.fit(X_train, y_train,verbose = 1)
        
        
        best_random = grid_obj_xgb.best_estimator_
        
        # In[Evaluate the prediction]
        val_pred = best_random.predict(X_val)
        tra_pred = best_random.predict(X_train)
        
        val_predict = pd.DataFrame({'prediction':val_pred})
        val_predict = pd.concat([df_val[['datetime', 
                                         'price_change_forward_ratio']].reset_index(drop=True),
                                       val_predict], axis = 1)
        
        tra_predict = pd.DataFrame({'prediction':tra_pred})
        tra_predict = pd.concat([df_train[['datetime', 
                                           'price_change_forward_ratio']].reset_index(drop=True), 
                                       tra_predict], axis = 1)
        
        val_predict.to_csv("data/xgboost_val_pred.csv", index=False)
        tra_predict.to_csv("data/xgboost_tra_pred.csv", index=False)
        
        
        # In[plot build in feature importance]
        # best_random.__dir__()
        # plot with sort
        sorted_idx = best_random.feature_importances_.argsort()
        plt.barh(np.array(features)[sorted_idx], best_random.feature_importances_[sorted_idx])
        plt.xlabel("Xgboost Feature Importance")
        
        # In[Use SHAP]
        # use SHAP as feature importance
        explainer = shap.TreeExplainer(best_random)
        shap_values = explainer.shap_values(X_train)
        
        # variable importace bar
        shap.summary_plot(shap_values, df_train[features], plot_type="bar")
        
        # SHAP value bar
        shap.summary_plot(shap_values, df_train[features])
        
        # Dependence plot from SHAP
        shap.dependence_plot("RSI", shap_values,df_train[features])
        
        
        # In[Remodel with best parameters]
        # Check with partial dependence
        xgb.XGBRegressor(parameters = grid_obj_xgb.best_params_)
        xgb_model = xgbr.fit(X_train, y_train,eval_set=[(X_train, y_train), (X_val, y_val)])
        
        fig, ax = plt.subplots(figsize=(40, 20))
        plot_partial_dependence(xgb_model, df_train[features], features, ax=ax,
                                grid_resolution=50, n_cols=6) 









