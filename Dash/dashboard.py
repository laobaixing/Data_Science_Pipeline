"""

Generate dashboard for stock


"""

from dash import Dash, dcc, html, dash_table
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from datetime import datetime
import pandas as pd


class StockDashBoard():
    
    def stock_chart(self, input_data_file):
        app = Dash()
        stocks_df = pd.read_csv(input_data_file)
        stocks_df.index = stocks_df.datetime
        nsdq = stocks_df['symbol'].unique()
        
        summary = pd.read_csv('output/summary_variable.csv')        
        for col in summary.columns[1:]:
            summary[col] = summary[col].round(2) 
        summary['count'] = [int(x) for x in summary['count']]
        
        # In[Find the continuous variable and categorical variable]

        data_types = stocks_df.dtypes.astype(str) # need to change to string for isin

        cont_vars = data_types[data_types.isin(["float64", "int64"])].index.to_list()
                               
        cate_vars = data_types[data_types == 'object'].index.to_list()
        cate_vars = cate_vars[2:]
        
        
        bivar_res = pd.read_excel('output/stock_bivar_analysis.xlsx')
        for col in bivar_res.columns[1:]:
            bivar_res[col] = bivar_res[col].round(3) 
        bivar_res.columns.values[0] = 'predictors'
        
        
        # Generate options for stock chart
        options = []
        for tic in nsdq:
            options.append({'label':'{}'.format(tic), 'value':tic})
            
        # Generate options for EDA
        cont_var_options = []
        for var in cont_vars:
            cont_var_options.append({'label':'{}'.format(var), 'value':var})
        
        app.layout = html.Div([
            dcc.Tabs([
                dcc.Tab(label = 'Stock chart', children = [
                html.Div([
                    html.Div([
                        html.H3('Select stock symbols:', style={'paddingRight':'30px'}),
                        # replace dcc.Input with dcc.Options, set options=options
                        dcc.Dropdown(
                            id='my_ticker_symbol',
                            options=options,
                            value=['TSLA'],
                            multi=True
                        )
                    # widen the Div to fit multiple inputs
                    ], style={'display':'inline-block', 'verticalAlign':'top', 
                              'width':'30%'}),
                              
                    html.Div([
                        html.H3('Select start and end dates:'),
                        dcc.DatePickerRange(
                            id='my_date_picker',
                            min_date_allowed=datetime(2017, 1, 1),
                            max_date_allowed=datetime.today(),
                            start_date=datetime(2018, 1, 1),
                            end_date=datetime.today()
                        )
                    ], style={'display':'inline-block'}),
                    
                    html.Div([
                        html.Button(
                            id='submit-button',
                            n_clicks=0,
                            children='Update',
                            style={'fontSize':18, 'marginLeft':'30px'}
                        ),
                    ], style={'display':'inline-block'}),
                    
                    dcc.Graph(
                        id='stock_chart',
                        figure={
                            'data': [
                                {'x': [1,2], 'y': [3,1]}
                            ]
                        }
                    )
                ])
                ]),
                
                dcc.Tab(label = "Summary", children = [
                html.Div([
                    dash_table.DataTable(data = summary.to_dict('records'), 
                                         columns = [{"name": i, "id": i} 
                                                    for i in summary.columns],
                                         id= 'tbl')
                    ])
                ]),
                
                dcc.Tab(label = "Bivariate analysis", children = [
                html.Div([
                    dash_table.DataTable(data = bivar_res.to_dict('records'))
                    ])
                ]),
                
                dcc.Tab(label = "variable distribution", children = [
                    html.Div([
                        html.Div([
                            html.H3('Select continuous variables:', 
                                    style={'paddingRight':'30px'}),
                            dcc.Dropdown(
                                id='continuous_vars',
                                options= cont_var_options,
                                value=['open'],
                                multi= False
                            )
                        # widen the Div to fit multiple inputs
                        ], style={'display':'inline-block', 
                                  'verticalAlign':'top', 'width':'30%'}),
                                               
                        dcc.Graph(id = 'QQ_plot'),
                        
                        dcc.Graph(id='histogram')                        
                        
                    ])
                ])
            ])
        ])
        
        @app.callback(
            Output('stock_chart', 'figure'),
            [Input('submit-button', 'n_clicks')],
            [State('my_ticker_symbol', 'value'),
            State('my_date_picker', 'start_date'),
            State('my_date_picker', 'end_date')])
        def update_graph(n_clicks, stock_ticker, start_date, end_date):
            start = datetime.strptime(start_date[:10], '%Y-%m-%d')
            end = datetime.strptime(end_date[:10], '%Y-%m-%d')
            # since stock_ticker is now a list of symbols, create a list of traces
            stocks_df['datetime'] = pd.to_datetime(stocks_df['datetime'])
            
            traces = []
            for i, tic in enumerate(stock_ticker):                
                df = stocks_df[stocks_df['symbol'] == tic]
                df = df[(df['datetime'] > start) & (df['datetime'] < end)] 
                traces.append(go.Scatter(x= df.index, y = df.close, name= tic+' close'))
                if i == 0:
                    traces.append(go.Bar(x= df.index, y = df.volume,opacity=0.65,
                                     name= tic+' volume'))
                
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            
            for i, trace in enumerate(traces):
                if i == 1:
                   fig.add_trace(traces[1],secondary_y = True) 
                else:
                    fig.add_trace(trace,secondary_y = False)                
            
            # Add figure title
            fig.update_layout(
                title_text= ', '.join(stock_ticker)
            )
            
            return fig
        
        @app.callback(
            Output('QQ_plot', 'figure'),
            Output('histogram', 'figure'),            
            Input('continuous_vars', 'value'))
        def update_histogram(variable):
            traces = []
            traces.append(go.Histogram(x = stocks_df[variable]))
                           
            from statsmodels.graphics.gofplots import qqplot
            
            var_value = stocks_df[variable].dropna()
            from scipy.stats import shapiro
            stat, p = shapiro(var_value)
            
            qqplot_data = qqplot(var_value, line='s').gca().lines
            
            fig1 = go.Figure()

            fig1.add_trace({
                'type': 'scatter',
                'x': qqplot_data[0].get_xdata(),
                'y': qqplot_data[0].get_ydata(),
                'mode': 'markers',
                'marker': {
                    'color': '#19d3f3'
                }
            })

            fig1.add_trace({
                'type': 'scatter',
                'x': qqplot_data[1].get_xdata(),
                'y': qqplot_data[1].get_ydata(),
                'mode': 'lines',
                'line': {
                    'color': '#636efa'
                }
            
            })

            fig1['layout'].update({
                'title': 'Quantile-Quantile Plot,' + ' Shapiro p: ' + 
                        "%.3f" % round(p, 3),
                'xaxis': {
                    'title': 'Theoritical Quantities',
                    'zeroline': False
                },
                'yaxis': {
                    'title': 'Sample Quantities'
                },
                'showlegend': False,
            })
            
            fig2 = {
                # set data equal to traces
                'data': traces,
                # use string formatting to include all symbols in the chart title
                'layout': {'title': variable +' histogram'}
            }
            
            return fig1, fig2

        
        app.run_server(port = 8050)
        
