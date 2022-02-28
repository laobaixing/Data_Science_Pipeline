"""

Generate dashboard for stock


"""

from dash import Dash, dcc, html
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
        
        options = []
        for tic in nsdq:
            options.append({'label':'{}'.format(tic), 'value':tic})
        
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
                    ], style={'display':'inline-block', 'verticalAlign':'top', 'width':'30%'}),
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
                        id='my_graph',
                        figure={
                            'data': [
                                {'x': [1,2], 'y': [3,1]}
                            ]
                        }
                    )
                ])
                ])
            ])
        ])
        
        @app.callback(
            Output('my_graph', 'figure'),
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
        
        
        app.run_server()

