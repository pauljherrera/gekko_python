from flask import Flask, jsonify, request
from dateutil import parser
import pandas as pd
import math
import os



app = Flask(__name__)

# Global variables.
prices = pd.DataFrame(columns=['open', 'high', 'low', 'close',
                               'vwp', 'volume', 'trades', 'datetime'])

bars = set()
in_market = False


def reset_settings():
    global prices, bars, in_market

    prices = pd.DataFrame(columns=['open', 'high', 'low', 'close',
                                   'vwp', 'volume', 'trades', 'datetime'])
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
    global prices, bars, in_market

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
            strategy = pd.DataFrame({'date': [time1],
                                        'tend':[a],
                                        'MAdif':[MAdif],
                                        'trade': [settings['trades']],
                                        },columns=['date', 'tend', 'MAdif', 'trade'],
                                        index=[date])
            strategy.to_csv('./static/MAdif.csv', mode='a+')
            # print('Malong: \n', MAlong)
            print('last MAlong: ', MAlong[lenght])
            # print('MAshort: \n', MAshort)
            print('last MAshort: ', MAshort[lenght])
            print('MAdif: ', MAdif)
            print('saved in MAdif.csv: ', strategy)
    else:
        # the strategy with a currency other than btc
        strategy_scv = pd.read_csv('./static/MAdif.csv')
        fstrategy = set(strategy_scv.loc[:,'date'])  # MAdif date
        tprices = str(parser.parse(prices.iloc[-1]['datetime']))  # date of candle
        # if there is a purchase or sale of another currency equal to the strategy
        if tprices in fstrategy:
            # the advice that return with candle for the gekko console
            col = strategy_scv[strategy_scv['date'] == tprices]
            advice = col.iloc[0]['tend']  # short/long
            # datastrategy: hour, tend, type
            if os.path.exists('static/advice.csv') and os.stat('./static/advice.csv').st_size > 0:
                datastrategy = pd.read_csv('./static/advice.csv')
                if datastrategy.iloc[-1]['tend'] != advice:
                    datastrategy = pd.DataFrame({
                                                'tend': [advice],
                                                'type': [settings['trades']]
                                                }, index=[tprices])
                    datastrategy.to_csv('./static/advice.csv', mode='a+')
                    advice = advice
                else:
                    pass
            else:
                if advice == 'short':
                    pass
                else:
                    datastrategy = pd.DataFrame({
                                                    'tend': [advice],
                                                    'type': [settings['trades']]
                                                    }, index=[tprices])
                    datastrategy.to_csv('./static/advice.csv', mode='a+')
                    advice = advice

            print("date coincident: ", tprices)
            print(advice)
        else:
            pass


    # Bullish signal.


    # Updating response body.
    body['trend'] = ''
    body['advice'] = advice
    
    return jsonify(body)

if __name__ == '__main__': 
    app.run() 