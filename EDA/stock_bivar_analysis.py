#!/usr/bin/env python
"""
Bivarate analysis
1. Check the relationship between dependent variable and predictors
2. Generate summary table

"""

import pandas as pd

pd.set_option('display.max_columns', 100)

import statsmodels.api as sm
from statsmodels.formula.api import ols


class StockBivariateAnalysis():
    def bivar_analysis(self, input_data_file, output_file):
        stocks_df = pd.read_csv(input_data_file)  #"data/stock_price.csv"

        data_types = stocks_df.dtypes.astype(str)

        cont_vars = data_types[data_types.isin(["float64",
                                                "int64"])].index.to_list()

        cate_vars = data_types[data_types == 'object'].index.to_list()
        cate_vars = cate_vars[1:]

        var_pvalues = {}

        print('\n Get continuous bivariate p value')
        for var in cont_vars:
            model = ols("price_return ~ " + var, data=stocks_df).fit()
            var_pvalues[var] = [model.pvalues[var], model.params[var]]

        print("\n Get Categorical bivariate p value")
        for var in cate_vars:
            model = ols("price_return ~ " + var, data=stocks_df).fit()
            anova_table = sm.stats.anova_lm(model, typ=2)
            var_pvalues[var] = [anova_table.values[0, 3], None]

        var_pvalues = pd.DataFrame.from_dict(var_pvalues,
                                             orient='index',
                                             columns=['p_value', 'coefs'])

        var_pvalues = var_pvalues.sort_values('p_value')

        # In[Output to the workbook]
        # 'output/stock_bivar_analysis.xlsx'
        with pd.ExcelWriter(output_file) as writer:
            var_pvalues.to_excel(writer,
                                 sheet_name='bivar_analysis',
                                 index=True)
