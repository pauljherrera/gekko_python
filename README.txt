Instructions:

1- Gekko server:
	Run "node gekko --ui" from the folder /gekko.
2- Flask server:
    Run "python 2assets_MA.py" from the folder /python_gekko.
3- Backtesting:
	- Open the Gekko UI from the browser using the URL "localhost:3000"
	- On the "Backtest" section choose the dataset of the base cryptocurrency to generate the entry signals with.
	- On the "Parameters" window, "signal" must be "yes".
	- Push the "Backtest" button. All the signals will be generated and stored in a .csv file.
	- For the second run, the trades will be done and the backtest will show the results. Choose the dataset of the cryptocurrency to trade with.
	- On the "Parameters" window, "signal" must be "no".
	- Push the "Backtest" button. The UI will show the results of the backtest.


