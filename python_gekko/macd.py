from flask import Flask, jsonify, request



app = Flask(__name__) 

@app.route('/macd', methods=['POST']) 
def strategy(): 
    advice = {'long': False,
              'short': False}

    # Getting request data.
    body = request.get_json()
    macddiff = body['macddiff']
    settings = body['settings']
    trend = body['trend']

    # Strategy logic.

    # Bullish signal.
    if macddiff > settings['thresholds']['up']:

        # New trend detected.
        if trend['direction'] != 'up':
            trend = {
                'duration': 0,
                'persisted': False,
                'direction': 'up',
                'adviced': False
            }

        trend['duration'] += 1

        # Analyzing data in order to send signals.
        if trend['duration'] >= settings['thresholds']['persistence']:
            trend['persisted'] = True

        if trend['persisted'] and not trend['adviced']:
            trend['adviced'] = True
            advice['long'] = True

    # Bearish signal.
    elif macddiff < settings['thresholds']['down']:

        # New trend detected.
        if trend['direction'] != 'down':
            trend = {
                'duration': 0,
                'persisted': False,
                'direction': 'down',
                'adviced': False
            }

        trend['duration'] += 1

        # Analyzing data in order to send signals.
        if trend['duration'] >= settings['thresholds']['persistence']:
            trend['persisted'] = True

        if trend['persisted'] and not trend['adviced']:
            trend['adviced'] = True
            advice['short'] = True

    # Updating response body.
    body['trend'] = trend
    body['advice'] = advice
    print(body)
 
    return jsonify(body)

if __name__ == '__main__': 
    app.run() 
