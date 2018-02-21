from flask import Flask, jsonify, request
from dateutil import parser
import pandas as pd



app = Flask(__name__)

# Global variables.
prices = pd.DataFrame(columns=['open', 'high', 'low', 'close',
                               'vwp', 'volume', 'trades'])
bars = set()
in_market = False


def reset_settings():
    global prices, bars, in_market

    prices = pd.DataFrame(columns=['open', 'high', 'low', 'close',
                                   'vwp', 'volume', 'trades'])
    bars = set()
    in_market = False


@app.route('/macd', methods=['POST']) 
def strategy(): 
    global prices, bars, in_market

    # Getting request data.
    body = request.get_json()
    # print(body)
    counter = int(body['counter'])
    settings = body['settings']
    print(settings)
    candle = body['candle']
    advice = {'long': False,
              'short': False}

    # Reseting when it's a new backtest.
    if counter == 1:
        reset_settings()

    # Storing new price.
    time = parser.parse(candle['start'])
    id = candle['id']
    new_price = pd.DataFrame({'open': candle['open'], 
                              'high': candle['high'],
                              'low': candle['low'],
                              'close': candle['close'],
                              'vwp': candle['vwp'],
                              'volume': candle['volume'],
                              'trades': candle['trades'],
                              }, 
                             index = [id])
    prices = prices.append(new_price)

    # Strategy logic.
    MovinAverage = prices['close'].rolling(10).mean()
    MovinAverage20 = prices['close'].rolling(20).mean()
    # print(MovinAverage)
    # print(MovinAverage20)

    # Bullish signal.


    # Updating response body.
    body['trend'] = ''
    body['advice'] = ''
    # print(prices)
    # print('prueba')
 
    return jsonify(body)

if __name__ == '__main__': 
    app.run() 
