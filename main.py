# coding: utf-8
import pandas as pd
import talib
import numpy as np #computing multidimensionla arrays
import datetime
import urllib3
import time
import settings

#################################### Logging #################################################
import logging
logging.basicConfig(filename='null',format='%(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

#create a file handler
handler = logging.FileHandler('logfile.log')
handler.setLevel(logging.INFO)

#create a logging format
title = logging.Formatter('%(message)s')
handler.setFormatter(title)

# add the handlers to the logger
logger.addHandler(handler)
##############################################################################################

# Initialize Client and connect to Binance
from binance.client import Client
client = Client()

# StochasticRSI Function
def Stoch(close,high,low, smoothk, smoothd, n):
    lowestlow = pd.Series.rolling(low,window=n,center=False).min()
    highesthigh = pd.Series.rolling(high, window=n, center=False).max()
    K = pd.Series.rolling(100*((close-lowestlow)/(highesthigh-lowestlow)), window=smoothk).mean()
    D = pd.Series.rolling(K, window=smoothd).mean()
    return K, D

#################################### Logging #################################################
logger.info("Date                    Close         RSI           %K             %D             EMA_200             EMA_40")
info = logging.Formatter('%(asctime)s %(message)s ','%Y-%m-%d %H:%M:%S')
handler.setFormatter(info)
logger.addHandler(handler)
##############################################################################################

# Main program
while True:
    # ping client to avoid timeout
    client = Client()

    # Get Binance Data into dataframe
    candles = client.get_klines(symbol='SOLUSDT', interval=Client.KLINE_INTERVAL_15MINUTE)
    df = pd.DataFrame(candles)
    df.columns=['timestart','open','high','low','close','?','timeend','?','?','?','?','?']
    df.timestart = [datetime.datetime.fromtimestamp(i/1000) for i in df.timestart.values]
    df.timeend = [datetime.datetime.fromtimestamp(i/1000) for i in df.timeend.values]

    # Compute RSI after fixing data
    float_data = [float(x) for x in df.close.values]
    np_float_data = np.array(float_data)
    rsi = talib.RSI(np_float_data, 14)
    df['rsi'] = rsi

    # Compute StochRSI using RSI values in Stochastic function
    mystochrsi = Stoch(df.rsi, df.rsi, df.rsi, 3, 3, 14)
    df['MyStochrsiK'],df['MyStochrsiD'] = mystochrsi

#################################### End of Main #############################################
# WARNING: If Logging is removed uncomment the next line.
# time.sleep(1) # Sleep for 1 second. So IP is not rate limited. Can be faster. Up to 1200 requests per minute.

#################################### Logging #################################################
    newestcandlestart = df.timestart.astype(str).iloc[-1] #gets last time
    newestcandleend = df.timeend.astype(str).iloc[-1] #gets current time?
    newestcandleclose = df.close.iloc[-1] #gets last close
    newestcandleRSI = df.rsi.astype(str).iloc[-1] #gets last rsi
    newestcandleK = df.MyStochrsiK.astype(str).iloc[-1] #gets last rsi
    newestcandleD = df.MyStochrsiD.astype(str).iloc[-1] #gets last rsi
    ema_200 = df['close'].ewm(span=200, adjust=False).mean().astype(str).iloc[-1] #200 SMA
    ema_40 = df['close'].ewm(span=40, adjust=False).mean().astype(str).iloc[-1] #40 SMA

    #Sleeps every 29 seconds and wakes up to post to logger.
    t = datetime.datetime.utcnow()
    sleeptime = (t.second)
    if sleeptime == 0 or sleeptime ==900:
        logger.info(newestcandleclose + " "
                    + newestcandleRSI + " "
                    + newestcandleK + " "
                    + newestcandleD + " "
                    + ema_200 + " "
                    + ema_40
                    )
        time.sleep(898)
##############################################################################################
