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
    Estrategia para indicar si comprar o vender en una determinada moneda
    con respecto al un MA de BTC.

    :param settings: configuracion para los calculos
    :param counter: evita la repeticion de data en el DaaFrame
    :param candle: velas del activo a procesar
    :param advice: indica comprar(long) o vender(short)
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
            # determina si es compra o venta
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
            print('guardado en .csv: ', estrategia)
        else:  # if override != 'yes'
            pass
        return jsonify(body)
    else:
        # la estrategia con una moneda distinta al btc
        estrategia_scv = pd.read_csv('./static/MAdif.csv')
        fstrategy = parser.parse(estrategia_scv.iloc[0]['fecha'])  # fecha del MAdif
        tprices = parser.parse(prices.iloc[-1]['datetime'])  # fecha de la vela
        print(estrategia_scv)
        # si existe una compra o venta de otra moneda igual a la estrategia
        if fstrategy == tprices:
            lista = []
            for key, value in candle.items():
                temp = [key, value]
                lista.append(temp)
            # el advice que retorna con la vela por la consola de gekko
            advice = estrategia_scv.iloc[0]['tend']  # short/long
            # datastrategy: madif, hora, tend, criptomoneda, candle
            datastrategy = pd.DataFrame({
                                        'hora': [fstrategy],
                                        'tend': [advice],
                                        'type': [settings['type']],
                                        'candle': [lista] })
            datastrategy.to_csv('./static/advice.csv')
            read_datastrategy = pd.read_csv('./static/advice.csv')
            json_datastrategy= read_datastrategy.to_json(orient='index')
            print("fecha del MAdif: ", fstrategy)
            print("fecha coincidente: ", tprices)
            print(advice)
            print(json_datastrategy)
            # prueba que muestra un body de un dataframe de la estrategia
            #body = json_datastrategy
            #return jsonify(body)

        else:
            # advice = 'nothing'
            return jsonify(body)


    # Bullish signal.


    # Updating response body.
    #body['trend'] = ''
    #body['advice'] = advice
    # print(prices)
    # print(len(prices))
    #print(fstrategy)
    #print(tprices)
 
    #return jsonify(body)

if __name__ == '__main__': 
    app.run() 
