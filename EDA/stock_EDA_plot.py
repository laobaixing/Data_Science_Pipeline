#!/usr/bin/env python

"""
Explore the stock predictors vs. price change ratio
With:
   Boxplot
   Scatter plot
   histogram
"""

from matplotlib import pyplot as plt
import pandas as pd
import os

basic_folder = os.getcwd()
basic_folder = basic_folder.split("\\")
basic_folder = "/".join(basic_folder[:3]+['OneDrive','stock_analysis'])
os.chdir(basic_folder)

stocks_df = pd.read_csv("data/stock_price.csv")
stocks_df.describe().transpose().to_csv("output/summary_variable.csv")

# In[Find the continuous variable and categorical variable]

data_types = stocks_df.dtypes.astype(str) # need to change to string for isin

cont_vars = data_types[data_types.isin(["float64", "int64"])].index.to_list()
                       
cate_vars = data_types[data_types == 'object'].index.to_list()
cate_vars = cate_vars[2:]

# In[reset index from 0]
stocks_df.index = range(len(stocks_df))

# In[Histogram of continuous variables]

from matplotlib.backends.backend_pdf import PdfPages
pp = PdfPages('output/Stock indicator histogram.pdf')

for var in cont_vars:
    fig = plt.figure()
    a = plt.hist(stocks_df[var])
    plt.title("histogram of "+ var)
    plt.ylabel("Count")
    pp.savefig(fig)
    plt.close(fig)
pp.close()



# In[scatter plot for continuous variables]:
pp = PdfPages('output/Stock indicator scatter.pdf')

for var in cont_vars:
    fig = plt.figure()
    a = plt.scatter(stocks_df[var], stocks_df["price_change_forward_ratio"], 
                    s=2)
    plt.title(var + " vs. price_change_forward_ratio")
    pp.savefig(fig)
    plt.close(fig)
pp.close()    
    

# In[Box plot for categorical variables]:
pp = PdfPages('output/Stock_categorical_indicator_boxplots.pdf')
for var in cate_vars:
    stocks_df.boxplot(column="price_change_forward_ratio", by = var)
    plt.title( "Boxplot on " + var + " indicator" )
    plt.ylabel('price_change_forward_ratio')
    plt.suptitle('')
    pp.savefig()
    plt.close()
pp.close()








