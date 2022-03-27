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
from sklearn import metrics

class ModelEvaluation():
    def __init__(self, model, val_pred_file = None, tra_pred_file = None):
        self.model = model
        if val_pred_file:
            self.val_predict = pd.read_csv(val_pred_file)
        if tra_pred_file:
            self.tra_predict = pd.read_csv(tra_pred_file) 
    
    def RMSE(self, output_file):
    
        # In[RMSE]
        
        val_rmse = round(metrics.mean_squared_error(self.val_predict['prediction'], 
                                       self.val_predict.price_return,
                                       squared = False), 4)
        tra_rmse = round(metrics.mean_squared_error(self.tra_predict['prediction'], 
                                       self.tra_predict.price_return,
                                       squared = False),4)
        
        rmse_tb = pd.DataFrame({'dataset':["train", "validation"],
                                'rmse':[tra_rmse, val_rmse],
                                'pred_mean':[self.tra_predict['prediction'].mean(),
                                             self.val_predict['prediction'].mean()],
                                'pred_std':[self.tra_predict['prediction'].std(),
                                             self.val_predict['prediction'].std()],
                                'price_change_ratio_mean':
                                    [self.tra_predict['price_return'].mean(),
                                     self.val_predict['price_return'].mean()],
                                'price_change_ratio_std':
                                    [self.tra_predict['price_return'].std(),
                                     self.val_predict['price_return'].std()]})
        with pd.ExcelWriter(output_file) as writer: 
            rmse_tb.to_excel(writer, sheet_name='RMSE', index=True)


    def corr(self, output_file):

        # In[Correlation between the prediction and the price change ratio]
        val_cor = np.corrcoef(self.val_predict['prediction'], 
                          self.val_predict['price_return'])
        tra_cor = np.corrcoef(self.tra_predict['prediction'], 
                          self.tra_predict['price_return'])
        
        cor_tb = pd.DataFrame({'dataset':["train", "validation"],
                                'cor_pred_ori':[tra_cor[0,1], val_cor[0,1]]})
        with pd.ExcelWriter('output/stock_mixed_model_evaluation.xlsx', mode="a") as writer:  
            cor_tb.to_excel(writer, sheet_name='Cor_pred_ori_depend', index=True)                

    def residual(self, port):
        from dash import Dash, dcc, html
        import plotly.express as px
        
        
        app = Dash()
        
        self.val_predict['resid'] = self.val_predict["price_return"] - \
                                self.val_predict['prediction']
                                
        self.tra_predict['resid'] = self.tra_predict["price_return"] - \
                                        self.tra_predict['prediction']
        
        fig_val_resid_return = px.scatter(self.val_predict, x="price_return", 
                         y="resid", 
                         labels={
                     "price_return": "Five days return"}
                        )   
        fig_val_resid = px.histogram(self.val_predict, x= "resid")
        
        
        fig_tra_resid_return = px.scatter(self.tra_predict, x="price_return", 
                         y="resid", 
                         labels={
                     "price_return": "Five days return"}
                        )
        fig_tra_resid = px.histogram(self.tra_predict, x= "resid", 
                                     labels = {
                                         "resid" : "model residuals"})
       
        if self.model == "Mixed":
            app.layout = html.Div([
                html.H3(self.model + ' Model Evaluation', style={'paddingRight':'30px'}),
                dcc.Tabs([
                    dcc.Tab(label = 'Training Residuals', children = [
                    html.Div([
                        dcc.Graph(
                            id='tra_resid_return',
                            figure= fig_tra_resid_return
                        ),
                        
                        dcc.Graph(
                            id='tra_resid',
                            figure= fig_tra_resid
                        )
                        
                        ])
                    ]),
                    dcc.Tab(label = 'Validation Residuals', children = [
                    html.Div([
                        dcc.Graph(
                            id='val_resid_return',
                            figure= fig_val_resid_return
                        ),
                        
                        dcc.Graph(
                            id='val_resid',
                            figure= fig_val_resid
                        )
                        
                        ])
                    ])
                ])
            ])
        
        if self.model == "XGBoost":
            app.layout = html.Div([
                html.H3(self.model + ' Model Evaluation', style={'paddingRight':'30px'}),
                dcc.Tabs([
                    dcc.Tab(label = 'Training Residuals', children = [
                    html.Div([
                        dcc.Graph(
                            id='tra_resid_return',
                            figure= fig_tra_resid_return
                        ),
                        
                        dcc.Graph(
                            id='tra_resid',
                            figure= fig_tra_resid
                        )
                        ])
                    ]),
                    dcc.Tab(label = 'Validation Residuals', children = [
                    html.Div([
                        dcc.Graph(
                            id='val_resid_return',
                            figure= fig_val_resid_return
                        ),
                        
                        dcc.Graph(
                            id='val_resid',
                            figure= fig_val_resid
                        )
                        ])
                    ]),
                    dcc.Tab(label = 'Feature importance', children = [
                    html.Div([
                        html.Img(src='/assets/xgb_shap_feature_importance.png',
                                 style={'height':'50%', 'width':'50%'})
                        ])
                    ])
                ])
            ])
        
        app.run_server(port = port)

    



