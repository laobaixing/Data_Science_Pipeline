"""
Luigi pipeline

Combine multiple stock analysis steps together
"""

import luigi
from datetime import datetime

from data_processing.process_data import ProcessStockData
from data_processing.get_TD_data import ExtractTD
from EDA.stock_bivar_analysis import StockBivariateAnalysis
from Dash.dashboard import StockDashBoard
from model_building.mixed_LM import MixedLM
from model_building.stock_xgboost import XGBoostStock
from model_evaluation.evaluate_model import ModelEvaluation

class GetStockData(luigi.Task):   
    def requires(self):
        return None
    
    def output(self):
        return luigi.LocalTarget("log/GetStockData_%s.txt" 
                                 % datetime.now().strftime("%Y_%m_%d_%H_%M"))
    
    def run(self):
        stocks = ['$COMPX','TTD', 'AMD','MDB','TSLA', "AMZN", "TWLO","GOOG","NFLX","DIS",
                  "TSM","CRM", "SHOP","DOCU","ZS", "PLTR", "YEXT", "INTC", "MSFT", "FB", 
        	  "QCOM","AAPL","XOM","NVDA",'TWTR', 'SNAP', 'ADBE', 'INTU','TEAM','$SPX.X']
        task = ExtractTD()
        task.extract_TD_data(stocks, output_file = "data/stock_dict.pickle")
        
        with self.output().open('w') as out_file:
            out_file.write('Complete')

class ProcessData(luigi.Task):
    def requires(self):
        return GetStockData()
        # return None
    
    def output(self):
        return luigi.LocalTarget("log/ProcessData_%s.txt" 
                                 % datetime.now().strftime("%Y_%m_%d_%H_%M"))
    
    def run(self):
        
        task = ProcessStockData()
        task.dic_to_df(input_data_file = 'data/stock_dict.pickle', 
                       output_data_file = "data/stock_price.csv")
        
        with self.output().open('w') as out_file:
            out_file.write('Complete')


class BivarAnalysis(luigi.Task):
    def requires(self):
        return ProcessData()
    
    def output(self):
        return luigi.LocalTarget('log/BivarAnalysis_%s.txt' 
                                 % datetime.now().strftime("%Y_%m_%d_%H_%M"))
    
    def run(self):
        task = StockBivariateAnalysis()
        task.bivar_analysis(input_data_file = "data/stock_price.csv",
                            output_file = 'output/stock_univar_analysis.xlsx')
        
        with self.output().open('w') as out_file:
            out_file.write('Complete')

class DataDashBoard(luigi.Task):
    def requires(self):        
        return ProcessData()
    
    def output(self):
        return luigi.LocalTarget('log/DashBoard_%s.txt' 
                                 % datetime.now().strftime("%Y_%m_%d_%H_%M"))
    
    def run(self):
        task = StockDashBoard()
        task.stock_chart(input_data_file = 'data/stock_price.csv')
        
        with self.output().open('w') as out_file:
            out_file.write('Complete')

class XGBoostModel(luigi.Task):
    def requires(self):
        return ProcessData()
    
    def output(self):
        return luigi.LocalTarget('log/XGBoostModel_%s.txt' 
                                 % datetime.now().strftime("%Y_%m_%d_%H_%M"))
    
    def run(self):
        task = XGBoostStock()
        task.xgboost_stock(input_data_file = 'data/stock_price.csv')
        
        with self.output().open('w') as out_file:
            out_file.write('Complete')
                                 

class MixedModel(luigi.Task):
    def requires(self):
        return ProcessData()
    
    def output(self):
        return luigi.LocalTarget('log/MixedModel_%s.txt' 
                                 % datetime.now().strftime("%Y_%m_%d_%H_%M"))
    
    def run(self):
        task = MixedLM()
        task.mixed_lm(input_data_file = 'data/stock_price.csv')
        
        with self.output().open('w') as out_file:
            out_file.write('Complete')

class ModelDashBoard(luigi.Task):
    def requires(self):
        return [MixedModel(), XGBoostModel(), BivarAnalysis()]
    
    def output(self):
        return luigi.LocalTarget('log/ModelDashBoard_%s.txt' 
                                 % datetime.now().strftime("%Y_%m_%d_%H_%M"))
    
    def run(self):
        task = ModelEvaluation("data/mixed_lm_val_pred.csv", 
                               "data/mixed_lm_tra_pred.csv" )
        task.residual()
        
        with self.output().open('w') as out_file:
            out_file.write('Complete')

if __name__ == '__main__':
    luigi.build([DataDashBoard(), ModelDashBoard()],
                workers=4) # 
    # luigi.run()
