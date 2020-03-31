from splinter import Browser
from selenium import webdriver
import requests
import urllib
import calendar
import datetime as dt
from datetime import datetime
from datetime import timedelta
from alpha_vantage.timeseries import TimeSeries
from accountnumbers import *
import pytz, holidays


###### Add URL in Auth() ######
###### Add tickers ######
###### How many days ago was the last day the market was open? #######

tickers = ('AAPL')
last_trading_day = 1
endpoint = r'https://api.tdameritrade.com/v1/accounts/{' + TDAmeritradeAcctNum +'}'
#get access token from def Auth() and pass it to the header(s)
access_token = Auth()
headers = {'Authorization': 'Bearer {}'.format(access_token)}
header = {'Authorization': 'Bearer {}'.format(access_token),
          'Content-Type':'application/json'}




def Auth():
    new_url = ######################add auth URL###################
    parse_url = urllib.parse.unquote(new_url.split('code=')[1])

    # define the endpoint
    url = r'https://api.tdameritrade.com/v1/oauth2/token'
    
    # define the headers
    headers = {'Content-Type':'application/x-www-form-urlencoded'}
    
    #define the payload
    payload = {'grant_type':'authorization_code', 
               'access_type':'offline',
               'code':parse_url,
               'client_id':client_id,
               'redirect_uri':'http://localhost/test'}
    
    # post the data to get the token
    authReply = requests.post(url, headers = headers, data = payload)
    
    # convert JSON string to dictionary
    decoded_content = authReply.json()
    
    # grab the access token
    access_token = decoded_content['access_token']
    
    print('Auth Complete')
    
    return access_token


def After_Hours(now = None):
        if not now:
            now = dt.datetime.now(tz)
        openTime = dt.time(hour = 8, minute = 30, second = 0)
        closeTime = dt.time(hour = 15, minute = 0, second = 0)
        # If a holiday
        if now.strftime('%Y-%m-%d') in us_holidays:
            return True
        # If before 0930 or after 1600
        if (now.time() < openTime) or (now.time() > closeTime):
            return True
        # If it's a weekend
        if now.date().weekday() > 4:
            return True
        
        return False
    

def Buy_Order(header, ticker, qty, buy_limit):
    # define endpoint for saved order
    endpoint = r'https://api.tdameritrade.com/v1/accounts/{' + TDAmeritradeAcctNum +'}/orders'

    # define payload in JSON format
    payload = {
              "orderType": "LIMIT",
              "session": "NORMAL",
              "price": buy_limit,
              "duration": "DAY",
              "orderStrategyType": "SINGLE",
              "orderLegCollection": [
                {
                  "instruction": "Buy",
                  "quantity": qty,
                  "instrument": {
                    "symbol": ticker,
                    "assetType": "EQUITY"
                  }
                }
              ]
            }
    
    content = requests.post(url = endpoint, json = payload, headers = header)
    
    return
    
def Sell_Order(header, ticker, qty, sell_limit, stop_price):
    # define endpoint for saved order
    endpoint = r'https://api.tdameritrade.com/v1/accounts/{' + TDAmeritradeAcctNum + '}/orders'

    # define payload in JSON format
    payload = {
              "orderStrategyType": "OCO",
              "childOrderStrategies": [
                {
                  "orderType": "LIMIT",
                  "session": "NORMAL",
                  "price": sell_limit,
                  "duration": "DAY",
                  "orderStrategyType": "SINGLE",
                  "orderLegCollection": [
                    {
                      "instruction": "SELL",
                      "quantity": qty,
                      "instrument": {
                        "symbol": ticker,
                        "assetType": "EQUITY"
                      }
                    }
                  ]
                },
                {
                  "orderType": "STOP",
                  "session": "NORMAL",
                  "stopPrice": stop_price,
                  "duration": "DAY",
                  "orderStrategyType": "SINGLE",
                  "orderLegCollection": [
                    {
                      "instruction": "SELL",
                      "quantity": qty,
                      "instrument": {
                        "symbol": ticker,
                        "assetType": "EQUITY"
                          }
                        }
                      ]
                    }
                  ]
                }
    
    content = requests.post(url = endpoint, json = payload, headers = header)

def Get_Close(ticker, last_trading_day):
    # initiate stock data
    ts = TimeSeries(key = timeserieskey, output_format = 'json')
    
    # get todays date time group
    timestamp = datetime.date(datetime.now())
    
    yesterday = timestamp - timedelta(days = last_trading_day)
    
    # change date formats
    yesterday = yesterday.strftime("%Y-%m-%d")
    
    daily_data = ts.get_daily_adjusted(ticker)
    # turn tuple into dict
    daily_price = daily_data[0]
    
    #extract yesterday's price in dict
    extract_close = dict((k, daily_price[k]) for k in [yesterday] 
                                            if k in daily_price) 
    
    prev_close = extract_close[yesterday]['4. close']
       
    print("Got yesterday's close"
    
    return prev_close

def Get_Open(ticker):
    endpoint = r"https://api.tdameritrade.com/v1/marketdata/{}/quotes".format(ticker)
    payload = {'apikey': client_id}
    content = requests.get(url = endpoint, params = payload)
    todays_open = content.json()
    todays_open = todays_open[ticker]['openPrice']
    
    print("Got today's open)
    
    return todays_open

def Fill_Price(ticker, get_orders):
    for order in orders:
        next_no = order['orderLegCollection'][0]['instrument']['symbol']
        if next_no == ticker:
            fill_price = order['orderActivityCollection'][0]['executionLegs'][0]['price']
                return fill_price 
            else:
                time.sleep(2)
                print('Trying to find order to create fill price for ' + ticker)
                Fill_Price(ticker)

def Get_Orders(headers):
    date = datetime.date(datetime.now())
    date = date.strftime("%Y-%m-%d")
    endpoint = r'https://api.tdameritrade.com/v1/accounts/{' + TDAmeritradeAcctNum + '}/orders'
    payload = {
              'maxResults': 100,
              'fromEnteredTime': date
              'toEnteredTime': date
              'status': 'FILLED'
              }
    
    content = requests.get(url = endpoint, params = payload, headers = headers)
    get_orders = content.json()
    
    return get_orders  
    



def Run(header, headers, tickers):
    market_time = After_Hours()
    if market_time == False:
        for ticker in tickers:
           # get yesterdays close and todays open
            prev_close = Get_Close(ticker, last_trading_day)
            print(prev_close)
            todays_open = Get_Open(ticker)
            print(todays_open)
            
            # begin the buy conditions
            if todays_open < prev_close:
            # get qty and buy_limit
                qty = 1000 / todays_open
                qty = round(qty)
                
                buy_limit = float(prev_close) - .01
                buy_limit = str(buy_limit)
                print(buy_limit)
                
                Buy_Order(header, ticker, qty, buy_limit)
                print('Buy Order Complete')
                
                get_orders = Get_Orders(headers)
                print('Got Latest Orders')
                
                fill_price = Fill_Price(ticker, get_orders)
                print('Got Fill Price')
                
                sell_limit = float(fill_price) * 1.01
                sell_limit = str(sell_limit)
                
                stop_price = float(fill_price) *.9
                stop_price = str(stop_price)
                
                ##calc sell_limit & stop_price
                Sell_Order(header, ticker, qty, sell_limit, stop_price)
                print('Sell Order Complete for ' + ticker)
                
                print('Time To Get Rich!')
    else:
        time.sleep(5)
        Run(tickers)
           
            
Run(tickers)



                
        
