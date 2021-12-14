import logging
import alpaca_trade_api as tradeapi
import time as _time
from datetime import datetime
from pytz import timezone
from datetime import timedelta
import requests
from datetime import time
import pandas as pd
import yfinance as yf
from xlwt import Workbook
from statistics import mean




#----------------vv Change Tickers To Whatever You Want vv-----------------------

#tickers = ['AAPL', 'ABBV', 'ABT', 'ADBE', 'AMD', 'AMZN', 'BA', 'BABA', 'BAC', 'BDX', 'BILI', 'BILL', 'BYND', 'CAT', 'CHWY', 'CMCSA', 'CMG', 'COUP', 'CRM', 'CRWD', 'CSCO', 'CVS', 'DIS', 'DKNG', 'DOCU', 'DT', 'ETSY', 'EXPI', 'F', 'FB', 'FDX', 'FNKO', 'FSLY', 'FVRR', 'GOOGL', 'GOOS', 'HD', 'HON', 'HUBS', 'INTC', 'ITW', 'JD', 'JNJ', 'JPM', 'KO', 'LRCX', 'MCD', 'MDT', 'MELI', 'MMM', 'MRNA', 'MS', 'MSFT', 'MSFT', 'MTCH', 'MU', 'NFLX', 'NIO', 'NKE', 'NOC', 'NVDA', 'OKTA', 'ORCL', 'OSTK', 'PEP', 'PFE', 'PG', 'PINS', 'PLTR', 'PYPL', 'QCOM', 'RH', 'ROKU', 'SBUX', 'SFIX', 'SFIX', 'SHAK', 'SHOP', 'SNAP', 'SPCE', 'SPOT', 'SQ', 'STNE', 'SYY', 'TEAM', 'TSLA', 'TTD', 'TWLO', 'UNH', 'UNP', 'V', 'WFC', 'WM', 'WMT', 'X', 'ZM', 'ZS']
tickers = ['AAPL','AMD','BILL','TEAM']
percgain = .04

#-----------------^^ Change % Gain To Whatever You Want ^^-----------------------



#--------------------Dont Mess With Anything Below Here--------------------------
#--------------------------------------------------------------------------------

highlist = []
lowlist = []
avghighlist = []
avglowlist = []
days = 125

def GetData(ticker):
    k = 5
    winner = 0
    loser = 0
    totaltriggered = 0
    gainer = 0
    lostest = 0
    try:
        tick = yf.Ticker(ticker)
        data = tick.history(period="130d", interval="1d", rounding=True)
        data = data.sort_values(['Date'] , ascending=[False])

        
        
        for i in range(days):
            topen = data.iloc[k-1]['Open']
            yclose = data.iloc[k]['Close']
            j = k
            for i in range(5):
                highs = data.iloc[j-1]['High']
                highlist.append(highs)
                j -= 1
                highoffivedays = max(highlist)
            j = k
            for i in range(5):
                lows = data.iloc[j-1]['Low']
                lowlist.append(lows)
                j -= 1
                lowoffivedays = min(lowlist)
             
            if topen < yclose:
                totaltriggered += 1
                averagetriggerhigh = (highoffivedays - topen) / topen
                avghighlist.append(averagetriggerhigh)
                testpercentgain = 1 + percgain
                testpercgain = topen * testpercentgain
                if highoffivedays > testpercgain:
                   winner += 1
                   gains = topen * percgain
                   gainer += gains
                   
                else: 
                   loser += 1
                   averagetriggerlow = (lowoffivedays - topen) / topen
                   avglowlist.append(averagetriggerlow)    
                   lost = (topen - lowoffivedays)
                   lostest += lost

            else:
                pass
                
            highlist.clear()
            lowlist.clear()
            k+=1
             
        avghigh = mean(avghighlist)
        avglow = mean(avglowlist)
        winavg = winner / totaltriggered
        onesharewinamount = gainer - lostest
        avghigh = avghigh * 100
        avglow = avglow * 100
        winavg = winavg * 100
        percreturn = onesharewinamount / topen * 100
        check = avghigh / avglow * -1
        percentagegain = percgain * 100

        #print('Checking ' + ticker)
        if onesharewinamount > 5:
            if percreturn > 8:
                print('----- ' + ticker + ' -----')
                print('Using A ' + str(percentagegain) + '% Gain As Win Criteria' )
                print(f"Win Amount Of 1 Share: ${onesharewinamount:.2f}")
                print(f"ROI Over 6 months: {percreturn:.2f}%")
                print(f"Avg Highs: {avghigh:.2f}%")
                print(f"Avg Lows: {avglow:.2f}%")
                print(f"Win % of times played: {winavg:.2f}%")
                print(f"Risk To Reward: {check:.2f}%")
                print(' ')
                
        avglowlist.clear()
        avghighlist.clear()
                
    except Exception as e:
        pass
    
        
for ticker in tickers:      
    GetData(ticker)     
        
        
        
        
        
        
        
        