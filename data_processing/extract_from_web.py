"""
This code define the functions for extracting data from XXX website 
 1. Set url to extract historical data,quote 
 2. Load as json 
 3. Change json to table
 4. merge and append the dataset

"""

import requests
import json
import pandas as pd
from datetime import date


def download_stock(endpoint, stock, td_consumer_key, period):
    full_url = endpoint.format(stock_ticker=stock,
                               periodType='year',
                               period=period,
                               frequencyType='daily',
                               frequency=1)
    page = requests.get(url=full_url, params={'apikey': td_consumer_key})
    content = json.loads(page.content)

    df = pd.json_normalize(content,
                           record_path=['candles'],
                           meta=['symbol', 'empty'],
                           meta_prefix='',
                           record_prefix='')

    df["datetime"] = pd.to_datetime(df['datetime'], unit="ms").dt.date
    return df


def download_quote(endpoint, stock, td_consumer_key):
    full_url = endpoint.format(stock_ticker=stock)
    page = requests.get(url=full_url, params={'apikey': td_consumer_key})
    df_quote = pd.read_json(page.content)
    return df_quote


def get_TD_stock_info(stock, period, history_data_link, quote_link,
                      td_consumer_key):

    df_history = download_stock(history_data_link, stock, td_consumer_key,
                                period)
    df_history = df_history.drop(columns=["empty"])
    df_quote = download_quote(quote_link, stock, td_consumer_key)

    if stock == '$SPX.X' or stock == '$COMPX':
        today_info = df_quote.loc[
            ['openPrice', 'highPrice', 'lowPrice', 'lastPrice', 'totalVolume'],
            stock]
    else:
        today_info = df_quote.loc[[
            'openPrice', 'highPrice', 'lowPrice', 'regularMarketLastPrice',
            'totalVolume'
        ], stock]
    today_info = today_info.to_list()
    df = df_history.append(
        {
            "datetime": pd.to_datetime(date.today()).date(),
            "open": today_info[0],
            "high": today_info[1],
            "low": today_info[2],
            "close": today_info[3],
            "volume": today_info[4],
            "symbol": stock
        },
        ignore_index=True)

    print("The most recent date is:" + str(max(df["datetime"])))

    return df
