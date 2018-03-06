from flask import Flask, jsonify, request
from dateutil import parser
import pandas as pd
import math
import os



app = Flask(__name__)

# Global variables.
prices = pd.DataFrame(columns=['open', 'high', 'low', 'close',
                               'vwp', 'volume', 'trades', 'datetime'])
new = pd.DataFrame(columns=['date', 'tend', 'MAdif'])
new_datastrategy = pd.DataFrame(columns=['tend'])

bars = set()
in_market = False


def reset_settings():
    global prices, bars, in_market, new, new_datastrategy

    prices = pd.DataFrame(columns=['open', 'high', 'low', 'close',
                                   'vwp', 'volume', 'trades', 'datetime'])
    new = pd.DataFrame(columns=['date', 'tend', 'MAdif'])
    new_datastrategy = pd.DataFrame(columns=['tend'])
    if os.path.exists('./static/advice.csv'):
        os.remove('./static/advice.csv')

    bars = set()
    in_market = False


@app.route('/macd', methods=['POST'])
def strategy():
    """
    Strategy to indicate whether to buy or sell in a certain crypto.

    :param settings: settings for calculations
    :param counter: avoid the repetition of data in the dataframe
    :param candle: candles of the assets to be processed
    :param advice: indicate buy(long) or sell(short)
    """
    global prices, bars, in_market, new, new_datastrategy

    # Getting request data.
    body = request.get_json()
    # print(body)
    counter = int(body['counter'])
    settings = body['settings']
    candle = body['candle']
    advice = {'long': False,
              'short': False}
    body['advice'] = advice

    # Reseting when it's a new backtest.
    if counter == 1:
        reset_settings()
    # Storing new price.
    time = parser.parse(candle['start'])
    # id = candle['id']
    new_price = pd.DataFrame({'open': candle['open'], 
                              'high': candle['high'],
                              'low': candle['low'],
                              'close': candle['close'],
                              'vwp': candle['vwp'],
                              'volume': candle['volume'],
                              'trades': candle['trades'],
                              'datetime': candle['start']
                              }, 
                             index = [time])
    prices = prices.append(new_price)
    # print(prices)
    # Strategy logic.
    if settings['signal'] == 'yes':
        # calculate for the MAdif
        malong = settings['long_period']
        MAlong = prices['close'].rolling(malong).mean()
        lenght = len(MAlong) - 1
        mashort = settings['short_period']
        MAshort = prices['close'].rolling(mashort).mean()
        lenght1 = len(MAshort) - 1
        # MAdif
        MAdif = (1 - (MAshort[lenght1]/MAlong[lenght]))*100
        # last date
        date = prices.iloc[-1]['datetime']
        time1 = parser.parse(date)  # date parsed
        # determines whether it is buying or selling
        entry_percentage = settings['entry_percentage']
        exit_percentage = settings['exit_percentage']
        if math.isnan(MAdif):
            a = 'nothing'
            pass
        else:
            if MAdif > entry_percentage and MAdif < exit_percentage:
                a = 'nothing'
            elif MAdif <= entry_percentage:
                a = 'long'
            elif MAdif >= exit_percentage:
                a = 'short'
        if a != 'nothing':
            strategy = pd.DataFrame({'date': [date],
                                        'tend':[a],
                                        'MAdif':[MAdif]
                                        },columns=['date', 'tend', 'MAdif'],
                                        index=[time1])
            new = new.append(strategy)
            print(new)
            new.to_csv('./static/MAdif.csv', mode='w+')
            # print('Malong: \n', MAlong)
            print('last MAlong: ', MAlong[lenght])
            # print('MAshort: \n', MAshort)
            print('last MAshort: ', MAshort[lenght])
            print('MAdif: ', MAdif)
            print('saved in MAdif.csv: ', strategy)
        else:
            pass
    else:
        # the strategy with a currency other than btc
        strategy_csv = pd.read_csv('./static/MAdif.csv')
        fstrategy = set(strategy_csv.loc[:,'date'])  # MAdif date
        tprices = str(prices.iloc[-1]['datetime'])  # date of candle
        # if there is a purchase or sale of another currency equal to the strategy
        if tprices in fstrategy:
            # the advice that return with candle for the gekko console
            row = strategy_csv[strategy_csv['date'] == tprices]
            advice = row.iloc[0]['tend']  # short/long
            # datastrategy: hour, tend, type
            if os.path.exists('./static/advice.csv') and os.stat('./static/advice.csv').st_size > 0:
                datastrategy = pd.read_csv('./static/advice.csv')
                if datastrategy.iloc[-1]['tend'] != advice:
                    datastrategy = pd.DataFrame({
                                                'tend': [advice],
                                                }, index=[tprices])
                    new_datastrategy = new_datastrategy.append(datastrategy)
                    new_datastrategy.to_csv('./static/advice.csv', mode='w+')
                    advice = advice
                else:
                    advice = {'long':False, 'short':False}
            else:
                if advice == 'short':
                    advice = {'long':False, 'short':False}
                else:
                    datastrategy = pd.DataFrame({
                                                    'tend': [advice],
                                                    }, index=[tprices])
                    new_datastrategy = new_datastrategy.append(datastrategy)
                    new_datastrategy.to_csv('./static/advice.csv', mode='w+')
                    advice = advice

            print("date coincident: ", tprices)
            print(advice)
        else:
            advice = {'long':False, 'short':False}


    # Bullish signal.


    # Updating response body.
    body['trend'] = ''
    body['advice'] = advice
    
    return jsonify(body)

if __name__ == '__main__': 
    app.run() 