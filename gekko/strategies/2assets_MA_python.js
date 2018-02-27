/*

Trading strategy for Python-Gekko.
Uses a MA crossover to calculate the difference between the two MA.
If the difference is bigger than X% on BTC, the strategy buys ETH.


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
  this.counter = 0;

  // how many candles do we need as a base
  // before we can start giving advice?
  this.requiredHistory = this.tradingAdvisor.historySize;
};

// what happens on every new candle?
method.update = function(candle) {

};

// for debugging purposes: log the last calculated
// EMAs and diff.
method.log = function() {

};

method.check = function(candle) {
  this.counter++;

  // Posting the required data so the Flask app can anlyze it.
  request.post('http://127.0.0.1:5000/macd', 
               {body: {
                  counter: this.counter,
                  settings: this.settings,
                  candle: this.candle,
                }, 
                json: true},
               function (error, response, body) {
                 // console.log(error);
                 // console.log(response);
                 console.log('body:', body); // Print the body

                  // Trading advice.
                  if(body === undefined){
                    console.log(error)
                  }else{
                    if (body.advice == 'long') {
                      this.advice('long');
                    } else if (body.advice == 'short') {
                      this.advice('short');
                    } else {
                      this.advice();
                    }
                  }
               }.bind(this)
  )
};

module.exports = method;
