from flask import Flask, jsonify, request
from dateutil import parser
import pandas as pd



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
    if settings['type'] == 'btc':
        if settings['override']  == 'yes':
            # calculate for the MAdif
            malong = settings['longperiod']
            MAlong = prices['close'].rolling(malong).mean()
            lenght = len(MAlong) - 1
            mashort = settings['shortperiod']
            MAshort = prices['close'].rolling(mashort).mean()
            lenght1 = len(MAshort) - 1
            # MAdif
            MAdif = (1 - (MAshort[lenght1]/MAlong[lenght]))*100
            # last date
            date = prices.iloc[-1]['datetime']
            time1 = parser.parse(date)  # date parsed
            # determines whether it is buying or selling
            if float(MAdif) > settings['percentage']:
                a = 'short'
            else:
                a = 'long'
            # for the strategy
            # nstrategy = {'date': date, 'tend': a, 'MAdif': MAdif, 'date': time1}
            # must be saved in a file advice.scv lenght, date, MAdif and a(advice)
            strategy = pd.DataFrame({'date': [date],
                                        'tend':[a],
                                        'MAdif':[MAdif]
                                        },columns=['date', 'tend', 'MAdif'],
                                        index=[time1])
            strategy.to_csv('./static/MAdif.csv')
            # print('Malong: \n', MAlong)
            print('last MAlong: ', MAlong[lenght])
            # print('MAshort: \n', MAshort)
            print('last MAshort: ', MAshort[lenght])
            print('MAdif: ', MAdif)
            print('saved in MAdif.csv: ', strategy)
        else:  # if override != 'yes'
            pass
        # return jsonify(body)
    else:
        # the strategy with a currency other than btc
        strategy_scv = pd.read_csv('./static/MAdif.csv')
        fstrategy = parser.parse(strategy_scv.iloc[0]['date'])  # date del MAdif
        tprices = parser.parse(prices.iloc[-1]['datetime'])  # date of candle
        print(strategy_scv)
        # if there is a purchase or sale of another currency equal to the strategy
        if fstrategy == tprices:
            lista = []
            for key, value in candle.items():
                temp = [key, value]
                lista.append(temp)
            # the advice that return with candle for the gekko console
            advice = strategy_scv.iloc[0]['tend']  # short/long
            # datastrategy: madif, hour, tend, criptomoneda, candle
            datastrategy = pd.DataFrame({
                                        'hora': [fstrategy],
                                        'tend': [advice],
                                        'type': [settings['type']],
                                        'candle': [lista] })
            datastrategy.to_csv('./static/advice.csv')
            read_datastrategy = pd.read_csv('./static/advice.csv')
            json_datastrategy= read_datastrategy.to_json(orient='index')
            print("date of MAdif: ", fstrategy)
            print("date coincidente: ", tprices)
            print(advice)
            print(json_datastrategy)
            # test that shows a body of a strategy dataframe
            #body = json_datastrategy
            #return jsonify(body)

        else:
            pass
            # return jsonify(body)


    # Bullish signal.


    # Updating response body.
    body['trend'] = ''
    body['advice'] = advice
    # print(prices)
    # print(len(prices))
    #print(fstrategy)
    #print(tprices)
 
    return jsonify(body)

if __name__ == '__main__': 
    app.run() 