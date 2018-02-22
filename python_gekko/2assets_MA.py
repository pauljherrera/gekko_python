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
    global prices, bars, in_market

    # Getting request data.
    body = request.get_json()
    # print(body)
    counter = int(body['counter'])
    settings = body['settings']
    candle = body['candle']
    advice = {'long': False,
              'short': False}

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
            # calculo para el MAdif
            malong = settings['longperiod']
            MAlong = prices['close'].rolling(malong).mean()
            indice = len(MAlong) - 1
            mashort = settings['shortperiod']
            MAshort = prices['close'].rolling(mashort).mean()
            indice1 = len(MAshort) - 1
            # MAdif
            MAdif = (1 - (MAshort[indice1]/MAlong[indice]))*100
            # ultima fecha
            fecha = prices.iloc[-1]['datetime']
            time1 = parser.parse(fecha)  # fecha parseada

            if float(MAdif) > settings['percentage']:
                a = 'long'
            else:
                a = 'short'
            # para la estrategia
            nestrategia = {'fecha': fecha, 'tend': a, 'MAdif': MAdif, 'date': time1}
            # se debe guardar en un archivo .scv indice, fecha, MAdif y a
            estrategia = pd.DataFrame({'fecha': [fecha],
                                        'tend':[a],
                                        'MAdif':[MAdif]
                                        },columns=['fecha', 'tend', 'MAdif'],
                                        index=[time1])
            estrategia.to_csv('./static/MAdif.csv')
            # print('Malong: \n', MAlong)
            print('último MAlong: ', MAlong[indice])
            # print('MAshort: \n', MAshort)
            print('último MAshort: ', MAshort[indice])
            print('MAdif: ', MAdif)
            print(a)
            print(time1)
            print(fecha)
            print(nestrategia)
            print(estrategia)
        else:  # if override != 'yes'
            pass
    else:
        estrategia_scv = pd.read_csv('./static/MAdif.csv')
        print(estrategia_scv)
        print(estrategia_scv.columns)


    # Bullish signal.


    # Updating response body.
    body['trend'] = ''
    body['advice'] = ''
    # print(prices)
    # print(len(prices))
 
    return jsonify(body)

if __name__ == '__main__': 
    app.run() 
