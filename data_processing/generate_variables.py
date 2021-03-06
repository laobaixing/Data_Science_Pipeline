"""
This code generates dependent variable and features
1. Generate the dependent variables: price change in five days
2. Generate the predictors 
3. Source of predictors
   a. From talib
   b. Calculate by the code

"""
import pandas as pd
import talib
import math


# In[Generate dependent variables]
def priceReturn(df, time_lag, price):
    df['price_change_forward'] = -df[price].diff(-5)
    df['price_return'] = df['price_change_forward'] / df[price]
    df['log_price_return'] = [math.log(x + 1) for x in df['price_return']]
    return df


# In[Generate features]
def get_ta_lib_indicator(df):
    df['RSI'] = talib.RSI(df['close'], timeperiod=14)
    df['MACD'], df['MACD_ewm9'], df['macdhist'] = talib.MACD(df['close'],
                                                             fastperiod=12,
                                                             slowperiod=26,
                                                             signalperiod=9)

    df['SAR'] = talib.SAR(df['high'], df['low'])
    df['upperband'], _, df['lowerband'] = talib.BBANDS(df['close'],
                                                       timeperiod=5,
                                                       nbdevup=2,
                                                       nbdevdn=2,
                                                       matype=0)
    df['mfi'] = talib.MFI(df['high'],
                          df['low'],
                          df['close'],
                          df['volume'],
                          timeperiod=14)
    df['ad'] = talib.AD(df['high'], df['low'], df['close'], df['volume'])

    df['dema_12'] = talib.TEMA(df['close'], timeperiod=12)
    df['dema_60'] = talib.TEMA(df['close'], timeperiod=60)

    df['kama_12'] = talib.KAMA(df['close'], timeperiod=12)
    df['kama_60'] = talib.KAMA(df['close'], timeperiod=60)

    # df['mama'], df['fama'] = talib.MAMA(df['close'], fastlimit=0, slowlimit=0)
    df['tema_12'] = talib.TEMA(df['close'], timeperiod=12)
    df['tema_60'] = talib.TEMA(df['close'], timeperiod=60)

    df['trima_12'] = talib.TRIMA(df['close'], timeperiod=12)
    df['trima_60'] = talib.TRIMA(df['close'], timeperiod=60)

    df['adx'] = talib.ADX(df['high'], df['low'], df['close'], timeperiod=14)
    df['aroondown'], df['aroonup'] = talib.AROON(df['high'],
                                                 df['low'],
                                                 timeperiod=20)

    df['slowk'], df['slowd'] = talib.STOCH(df['high'],
                                           df['low'],
                                           df['close'],
                                           fastk_period=5,
                                           slowk_period=3,
                                           slowk_matype=0,
                                           slowd_period=3,
                                           slowd_matype=0)

    df['obv'] = talib.OBV(df['close'], df['volume'])

    df['atr'] = talib.ATR(df['high'], df['low'], df['close'], timeperiod=14)
    df['natr'] = talib.NATR(df['high'], df['low'], df['close'], timeperiod=14)

    df['cdl2crows'] = talib.CDL2CROWS(df['open'], df['high'], df['low'],
                                      df['close'])
    df['cdl3blackcrows'] = talib.CDL3BLACKCROWS(df['open'], df['high'],
                                                df['low'], df['close'])
    df['cdl3inside'] = talib.CDL3INSIDE(df['open'], df['high'], df['low'],
                                        df['close'])
    df['cdl3starsinsouth'] = talib.CDL3STARSINSOUTH(df['open'], df['high'],
                                                    df['low'], df['close'])
    df['cdl3whitesoldiers'] = talib.CDL3WHITESOLDIERS(df['open'], df['high'],
                                                      df['low'], df['close'])
    df['cdldragonflydoji'] = talib.CDLDRAGONFLYDOJI(df['open'], df['high'],
                                                    df['low'], df['close'])
    df['cdlhikkake'] = talib.CDLHIKKAKE(df['open'], df['high'], df['low'],
                                        df['close'])
    df['cdlmathold'] = talib.CDLMATHOLD(df['open'],
                                        df['high'],
                                        df['low'],
                                        df['close'],
                                        penetration=0)

    return (df)


def add_ts_indicators(df):
    # These indicator also need to be calculated by stock
    # as they rely on time series

    df['ma13'] = df['close'].rolling(window=13).mean()
    df['ma60'] = df['close'].rolling(window=60).mean()
    df['ma200'] = df['close'].rolling(window=200).mean()

    df['vol_ave10'] = df['volume'].rolling(window=10).mean()
    df['vol_ratio'] = df['volume'] / df['vol_ave10']

    df["average_13_60_down"] = ((df.ma60 - df.ma13) > 0).astype("int64")
    df["average_13_60_down"] = ((df.shift(1).ma60 - df.shift(1).ma13) < 0).astype("int64")\
        * df["average_13_60_down"] #? should early one ma13 > ma 60
    df["average_13_60_down"] = 1-(1-df["average_13_60_down"])* \
        (1-df["average_13_60_down"].shift(1, fill_value=0))

    return df


def get_ext_indicator(df):
    # These indicator don't need the time series data
    df['day_high_low_diff'] = (df['high'] - df['low']) / df['close']

    df['RSI_ind'] = pd.cut(df.RSI, [0, 25, 50, 75, 100],
                           labels=["RSI_1", "RSI_2", "RSI_3", "RSI_4"])
    df["MACD_ind"] = pd.cut(df.MACD_ewm9, [-math.inf, -5, 0, 10, math.inf],
                            labels=["MACD_1", "MACD_2", "MACD_3", "MACD_4"])

    df['MACD_diff'] = df['MACD'] - df['MACD_ewm9']

    df['SAR_diff'] = df['close'] - df['SAR']
    df['SAR_diff_ind'] = df['SAR_diff'] >= 0

    df['B_upper_band_diff'] = df['close'] - df['upperband']
    df['B_lower_band_diff'] = df['close'] - df['lowerband']

    df['mfi_ind'] = pd.cut(df.mfi,
                           bins=[0, 20, 80, 100],
                           labels=['low', 'medium', 'high'])
    df['ad_ind'] = ['up' if x > 0 else 'down' for x in df.ad]

    df['RSI_cen'] = df.groupby('symbol').RSI.transform(lambda x: x - x.mean())

    df['ma13_diff_ratio'] = (df['close'] - df['ma13']) / df['ma13']
    df['ma60_diff_ratio'] = (df['close'] - df['ma60']) / df['ma60']
    df['ma200_diff_ratio'] = (df['close'] - df['ma200']) / df['ma200']

    df['dema_12_diff_ratio'] = (df['close'] - df['dema_12']) / df['dema_12']
    df['dema_60_diff_ratio'] = (df['close'] - df['dema_60']) / df['dema_60']
    df['dema_12_60_diff_ratio'] = (df['dema_12'] -
                                   df['dema_60']) / df['dema_60']

    df['kama_12_diff_ratio'] = (df['close'] - df['kama_12']) / df['kama_12']
    df['kama_60_diff_ratio'] = (df['close'] - df['kama_60']) / df['kama_60']
    df['kama_12_60_diff_ratio'] = (df['kama_12'] -
                                   df['kama_60']) / df['kama_60']

    df['tema_12_diff_ratio'] = (df['close'] - df['tema_12']) / df['tema_12']
    df['tema_60_diff_ratio'] = (df['close'] - df['tema_60']) / df['tema_60']
    df['tema_12_60_diff_ratio'] = (df['tema_12'] -
                                   df['tema_60']) / df['tema_60']

    df['trima_12_diff_ratio'] = (df['close'] - df['trima_12']) / df['trima_12']
    df['trima_60_diff_ratio'] = (df['close'] - df['trima_60']) / df['trima_60']
    df['trima_12_60_diff_ratio'] = (df['trima_12'] -
                                    df['trima_60']) / df['trima_60']

    return (df)
