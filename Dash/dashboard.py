"""

Generate dashboard for the data
with stock data as example


"""

from dash import Dash, dcc, html, dash_table
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import plotly.express as px
from datetime import datetime
import pandas as pd
import numpy as np

tabs_styles = {'height': '44px'}

tab_style = {
    'borderBottom': '1px solid #d6d6d6',
    'padding': '6px',
    'fontWeight': 'bold'
}

tab_selected_style = {
    'borderTop': '1px solid #d6d6d6',
    'borderBottom': '1px solid #d6d6d6',
    'backgroundColor': '#119DFF',
    'color': 'white',
    'padding': '6px'
}

# set the Div width to fit multiple inputs in a row
small_div_style = {
    'display': 'inline-block',
    'verticalAlign': 'top',
    'width': '30%'
}  # 30% mean occupy 30% width of row

H3_style = {'paddingRight': '30px'}

graph_config = {
    'toImageButtonOptions': {
        'format': 'svg',  # one of png, svg, jpeg, webp
        'filename': 'custom_image',
        'height': 500,
        'width': 700,
        'scale': 1  # Multiply title/legend/axis/canvas sizes by this factor
    }
}


def html_Div_table(data, id):
    obj = html.Div([
        dash_table.DataTable(data=data.to_dict('records'),
                             columns=[{
                                 "name": i,
                                 "id": i
                             } for i in data.columns],
                             id=id,
                             export_format="csv")
    ])
    return obj


class StockDashBoard():
    def EDA(self, input_data_file):
        app = Dash()
        stocks_df = pd.read_csv(input_data_file)
        stocks_df.datetime = pd.to_datetime(stocks_df.datetime,
                                            format="%Y-%m-%d")

        summary = stocks_df.describe(datetime_is_numeric=True)
        for col in summary.columns:
            if summary[col].dtype == 'float64':
                summary[col] = summary[col].round(2)
            if col == 'datetime':
                summary[col][1:] = pd.to_datetime(summary[col][1:],
                                                  format="%Y-%m-%d").dt.date
        summary = summary.transpose()
        summary['Missing'] = 1 - summary['count'] / stocks_df.shape[0]
        summary['count'] = [int(x) for x in summary['count']]
        summary['Missing'] = [
            str(round(x * 100, 2)) + '%' for x in summary['Missing']
        ]
        summary = summary.reset_index().rename(columns={'index': "var"})

        cate_summary = stocks_df.describe(include=np.object).transpose()
        cate_summary[
            'Missing'] = 1 - cate_summary['count'] / stocks_df.shape[0]
        cate_summary['Missing'] = [
            str(round(x * 100, 2)) + '%' for x in cate_summary['Missing']
        ]
        cate_summary = cate_summary.reset_index().rename(
            columns={'index': "var"})

        # In[Find the continuous variable and categorical variable]

        data_types = stocks_df.dtypes.astype(str)

        cont_vars = data_types[data_types.isin(["float64",
                                                "int64"])].index.to_list()

        cate_vars = data_types[data_types == 'object'].index.to_list()
        cate_vars = cate_vars[2:]

        bivar_res = pd.read_excel('output/stock_bivar_analysis.xlsx')
        for col in bivar_res.columns[1:]:
            bivar_res[col] = bivar_res[col].round(3)
        bivar_res.columns.values[0] = 'predictors'

        nsdq = stocks_df['symbol'].unique()
        # Generate options for stock chart
        symbol_options = []
        for tic in nsdq:
            symbol_options.append({'label': tic, 'value': tic})

        symbol_options2 = symbol_options
        symbol_options2.append({'label': 'all', 'value': 'all'})

        # Generate options for EDA
        cont_var_options = []
        for var in cont_vars:
            cont_var_options.append({'label': '{}'.format(var), 'value': var})

        cate_var_options = []
        for var in cate_vars:
            cate_var_options.append({'label': '{}'.format(var), 'value': var})

        app.layout = html.Div([
            dcc.Tabs([
                dcc.Tab(label='Stock chart',
                        children=[
                            html.Div([
                                html.Div([
                                    html.H3('Select stock symbols:',
                                            style=H3_style),
                                    dcc.Dropdown(id='my_ticker_symbol',
                                                 options=symbol_options,
                                                 value=['TSLA'],
                                                 multi=True)
                                ],
                                         style=small_div_style),
                                html.Div([
                                    html.H3('Select start and end dates:',
                                            style=H3_style),
                                    dcc.DatePickerRange(
                                        id='my_date_picker',
                                        min_date_allowed=datetime(2017, 1, 1),
                                        max_date_allowed=datetime.today(),
                                        start_date=datetime(2018, 1, 1),
                                        end_date=datetime.today())
                                ],
                                         style={'display': 'inline-block'}),
                                html.Div([
                                    html.Button(id='submit-button',
                                                n_clicks=0,
                                                children='Update',
                                                style={
                                                    'fontSize': 18,
                                                    'marginLeft': '30px'
                                                }),
                                ],
                                         style={'display': 'inline-block'}),
                                dcc.Graph(id='stock_chart',
                                          config=graph_config),
                            ])
                        ],
                        style=tab_style,
                        selected_style=tab_selected_style),
                dcc.Tab(label="Summary",
                        children=[
                            dcc.Tabs([
                                dcc.Tab(label='continuous',
                                        children=[
                                            html_Div_table(summary,
                                                           id='cont_summary')
                                        ],
                                        style=tab_style,
                                        selected_style=tab_selected_style),
                                dcc.Tab(label='categorical',
                                        children=[
                                            html_Div_table(cate_summary,
                                                           id='cate_summary')
                                        ],
                                        style=tab_style,
                                        selected_style=tab_selected_style)
                            ],
                                     style=tabs_styles)
                        ],
                        style=tab_style,
                        selected_style=tab_selected_style),
                dcc.Tab(
                    label="Bivariate analysis",
                    children=[
                        dcc.Tabs([
                            dcc.Tab(
                                label='Linear model',
                                children=[
                                    html_Div_table(bivar_res,
                                                   id='bivar_analysis')
                                ],
                                style=tab_style,
                                selected_style=tab_selected_style),
                            dcc.Tab(
                                label='Scatter plot',
                                children=[
                                    html.Div([
                                        html.H3(
                                            'Select continuous variables:',
                                            style=H3_style),
                                        dcc.Dropdown(
                                            id='continuous_predictors',
                                            options=cont_var_options,
                                            value=['open'],
                                            multi=False)
                                    ],
                                             style=small_div_style),
                                    dcc.Graph(id='bivar_scatter_plot',
                                              config=graph_config)
                                ],
                                style=tab_style,
                                selected_style=tab_selected_style),
                            dcc.Tab(
                                label='Box plot',
                                children=[
                                    html.Div([
                                        html.H3(
                                            'Select categorical variables:',
                                            style=H3_style),
                                        dcc.Dropdown(
                                            id='categorical_predictors',
                                            options=cate_var_options,
                                            value=['MACD_ind'],
                                            multi=False)
                                    ],
                                             style=small_div_style),
                                    dcc.Graph(id='box_plot',
                                              config=graph_config)
                                ],
                                style=tab_style,
                                selected_style=tab_selected_style)
                        ])
                    ],
                    style=tab_style,
                    selected_style=tab_selected_style),
                dcc.Tab(
                    label="Variable distribution",
                    children=[
                        dcc.Tabs([
                            dcc.Tab(
                                label='continuous variables',
                                children=[
                                    html.Div([
                                        html.H3('Select continuous variables:',
                                                style=H3_style),
                                        dcc.Dropdown(id='continuous_vars',
                                                     options=cont_var_options,
                                                     value=['open'],
                                                     multi=False)
                                    ],
                                             style=small_div_style),
                                    html.Div([
                                        html.H3('Select stock symbols:',
                                                style=H3_style),
                                        dcc.Dropdown(
                                            id='stock_symbol_4_cont_var',
                                            options=symbol_options2,
                                            value=['TSLA'],
                                            multi=False)
                                    ],
                                             style={'display': 'inline-block'
                                                    }),
                                    html.Div([
                                        html.Button(
                                            id='update_button_4_cont_var',
                                            n_clicks=0,
                                            children='Update',
                                            style={
                                                'fontSize': 18,
                                                'marginLeft': '30px'
                                            }),
                                    ],
                                             style={'display': 'inline-block'
                                                    }),
                                    dcc.Graph(id='QQ_plot',
                                              config=graph_config),
                                    dcc.Graph(id='histogram',
                                              config=graph_config),
                                    dcc.Graph(id='cont_var_time_trend',
                                              config=graph_config)
                                ],
                                style=tab_style,
                                selected_style=tab_selected_style),
                            dcc.Tab(
                                label='categorical variables',
                                children=[
                                    html.Div([
                                        html.H3(
                                            'Select categorical variables:',
                                            style=H3_style),
                                        dcc.Dropdown(id='categorical_vars',
                                                     options=cate_var_options,
                                                     value=['MACD_ind'],
                                                     multi=False)
                                    ],
                                             style=small_div_style),
                                    dcc.Graph(id='bar_plot',
                                              config=graph_config)
                                ],
                                style=tab_style,
                                selected_style=tab_selected_style)
                        ],
                                 style=tabs_styles)
                    ],
                    style=tab_style,
                    selected_style=tab_selected_style)
            ],
                     style=tabs_styles)
        ])

        @app.callback(Output('stock_chart', 'figure'),
                      [Input('submit-button', 'n_clicks')], [
                          State('my_ticker_symbol', 'value'),
                          State('my_date_picker', 'start_date'),
                          State('my_date_picker', 'end_date')
                      ])
        def update_graph(n_clicks, stock_ticker, start_date, end_date):
            start = datetime.strptime(start_date[:10], '%Y-%m-%d')
            end = datetime.strptime(end_date[:10], '%Y-%m-%d')
            # since stock_ticker is now a list of symbols, create a list of traces
            stocks_df['datetime'] = pd.to_datetime(stocks_df['datetime'])

            traces = []
            for i, tic in enumerate(stock_ticker):
                df = stocks_df[stocks_df['symbol'] == tic]
                df = df[(df['datetime'] > start) & (df['datetime'] < end)]
                traces.append(
                    go.Scatter(x=df.datetime, y=df.close, name=tic + ' close'))
                if i == 0:
                    traces.append(
                        go.Bar(x=df.datetime,
                               y=df.volume,
                               opacity=0.65,
                               name=tic + ' volume'))

            fig = make_subplots(specs=[[{"secondary_y": True}]])

            for i, trace in enumerate(traces):
                if i == 1:
                    fig.add_trace(traces[1], secondary_y=True)
                else:
                    fig.add_trace(trace, secondary_y=False)

            fig.update_layout(title_text=', '.join(stock_ticker))

            return fig

        @app.callback(Output('QQ_plot',
                             'figure'), Output('histogram', 'figure'),
                      Output('cont_var_time_trend', 'figure'),
                      [Input('update_button_4_cont_var', 'n_clicks')], [
                          State('continuous_vars', 'value'),
                          State('stock_symbol_4_cont_var', 'value')
                      ])
        def plot_cont_var(n_clicks, variable, symbol):

            from statsmodels.graphics.gofplots import qqplot

            if symbol == 'all':
                df = stocks_df
            else:
                df = stocks_df[stocks_df['symbol'] == symbol]
            # df = df.dropna(subset=['log_price_return', variable])

            var_value = df[variable].dropna()
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
                'title':
                'Quantile-Quantile Plot,' + ' Shapiro p: ' +
                "%.3f" % round(p, 3),
                'xaxis': {
                    'title': 'Theoritical Quantities',
                    'zeroline': False
                },
                'yaxis': {
                    'title': 'Sample Quantities'
                },
                'showlegend':
                False,
            })

            fig2 = px.histogram(df, variable)

            fig3 = px.scatter(df, x='datetime', y=variable)

            return fig1, fig2, fig3

        @app.callback(Output('bivar_scatter_plot', 'figure'),
                      Input('continuous_predictors', 'value'))
        def bivar_scatterplot(variable):

            df = stocks_df.dropna(subset=['log_price_return', variable])

            fig = px.scatter(df,
                             x=variable,
                             y='log_price_return',
                             trendline='ols',
                             trendline_color_override='orange')

            fig['layout'].update({
                'title': 'Predictor vs log return',
                'xaxis': {
                    'title': variable,
                    'zeroline': False
                },
                'yaxis': {
                    'title': 'Log Return'
                },
                'showlegend': False,
            })

            return fig

        @app.callback(Output('box_plot', 'figure'),
                      Input('categorical_predictors', 'value'))
        def box_plot(variable):

            df = stocks_df.dropna(subset=['log_price_return', variable])

            fig = px.box(df, x=variable, y='log_price_return')

            fig['layout'].update({
                'title': 'Predictor vs log return',
                'yaxis': {
                    'title': 'Log Return'
                },
                'showlegend': False,
            })

            return fig

        @app.callback(Output('bar_plot', 'figure'),
                      Input('categorical_vars', 'value'))
        def update_barplot(variable):
            perc = stocks_df.reset_index().groupby(
                variable, dropna=False)['index'].agg(['count'])
            perc = perc.reset_index()

            fig = px.bar(perc, x=variable, y='count')

            return fig

        app.run_server(port=8050)
