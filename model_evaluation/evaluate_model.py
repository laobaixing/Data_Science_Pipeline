"""
Evaluate the model result for stocks

Input:
    data/mixed_lm_val_pred.csv
    data/mixed_lm_tra_pred.csv
Output:
    output/stock_model_evaluation.xlsx

"""

import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error

class ModelEvaluation():
    def __init__(self, val_pred_file = None, tra_pred_file = None):
        if val_pred_file:
            self.val_predict = pd.read_csv(val_pred_file) #"data/mixed_lm_val_pred.csv"
        if tra_pred_file:
            self.tra_predict = pd.read_csv(tra_pred_file) #"data/mixed_lm_tra_pred.csv"
    
    def RMSE(self, output_file):
    
        # In[RMSE]
        
        val_rmse = round(mean_squared_error(self.val_predict['prediction'], 
                                       self.val_predict.price_change_forward_ratio,
                                       squared = False), 4)
        tra_rmse = round(mean_squared_error(self.tra_predict['prediction'], 
                                       self.tra_predict.price_change_forward_ratio,
                                       squared = False),4)
        
        rmse_tb = pd.DataFrame({'dataset':["train", "validation"],
                                'rmse':[tra_rmse, val_rmse],
                                'pred_mean':[self.tra_predict['prediction'].mean(),
                                             self.val_predict['prediction'].mean()],
                                'pred_std':[self.tra_predict['prediction'].std(),
                                             self.val_predict['prediction'].std()],
                                'price_change_ratio_mean':
                                    [self.tra_predict['price_change_forward_ratio'].mean(),
                                     self.val_predict['price_change_forward_ratio'].mean()],
                                'price_change_ratio_std':
                                    [self.tra_predict['price_change_forward_ratio'].std(),
                                     self.val_predict['price_change_forward_ratio'].std()]})
        with pd.ExcelWriter(output_file) as writer:  #'output/stock_mixed_model_evaluation.xlsx'
            rmse_tb.to_excel(writer, sheet_name='RMSE', index=True)


    def corr(self, output_file):

        # In[Correlation between the prediction and the price change ratio]
        val_cor = np.corrcoef(self.val_predict['prediction'], 
                          self.val_predict['price_change_forward_ratio'])
        tra_cor = np.corrcoef(self.tra_predict['prediction'], 
                          self.tra_predict['price_change_forward_ratio'])
        
        cor_tb = pd.DataFrame({'dataset':["train", "validation"],
                                'cor_pred_ori':[tra_cor[0,1], val_cor[0,1]]})
        with pd.ExcelWriter('output/stock_mixed_model_evaluation.xlsx', mode="a") as writer:  
            cor_tb.to_excel(writer, sheet_name='Cor_pred_ori_depend', index=True)                

    def residual(self):
        from dash import Dash, dcc, html
        import plotly.express as px
        
        app = Dash()  
        
        fig = px.scatter(self.val_predict, x="price_change_forward_ratio", 
                         y="prediction", 
                         labels={
                     "price_change_forward_ratio": "5 days price change ratio"}
                        )        
       
        app.layout = html.Div([
            dcc.Tabs([
                dcc.Tab(label = 'Validation Residuals', children = [
                html.Div([
                    dcc.Graph(
                        id='my_graph',
                        figure= fig
                    )
                ])
                ])
            ])
        ])
        
        app.run_server(port = 8000)

    



