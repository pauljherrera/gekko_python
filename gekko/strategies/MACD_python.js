/*

  MACD - DJM 31/12/2013

  (updated a couple of times since, check git history)

 */

// helpers
var _ = require('lodash');
var log = require('../core/log.js');
var request = require('request');

// let's create our own method
var method = {};

// prepare everything our method needs
method.init = function() {
  // keep state about the current trend
  // here, on every new candle we use this
  // state object to check if we need to
  // report it.
  this.trend = {
    direction: 'none',
    duration: 0,
    persisted: false,
    adviced: true
  };

  // how many candles do we need as a base
  // before we can start giving advice?
  this.requiredHistory = this.tradingAdvisor.historySize;

  // define the indicators we need
  this.addIndicator('macd', 'MACD', this.settings);
}

// what happens on every new candle?
method.update = function(candle) {

}

// for debugging purposes: log the last calculated
// EMAs and diff.
method.log = function() {
}

method.check = function() {
  var macddiff = this.indicators.macd.result;

  // Posting the required data so the Flask app can anlyze it.
  request.post('http://127.0.0.1:5000/macd', 
               {body: {
                  settings: this.settings,
                  macddiff: macddiff,
                  trend: this.trend,
                }, 
                json: true},
               function (error, response, body) {
    console.log('body:', body); // Print the body
    // Updating trend object.
    this.trend = body.trend

    // Trading advice.
    if (body.advice.long) {
      this.advice('long');
    } else if (body.advice.short) {
      this.advice('short');
    } else {
      this.advice();
    }
  }.bind(this)
)}

module.exports = method;
