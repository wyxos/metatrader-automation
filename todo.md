- Add support to provide success rate per channel
- Add support to allow choosing the account to send trade request per channel


Trade with DDXAUUSD sell 3133 sl 3143 tp1 3128 tp2 3123 tp3 3118{"signal": "sell", "symbol": "XAUUSD", "price": 3133.0, "sl": 3143.0, "tp": [1.0, 2.0, 3.0]}{"success": true, "result": {"retcode": 10009, "deal": 52276152441, "order": 52325188449, "volume": 0.01, "price": 3119.55, "bid": 3119.55, "ask": 3119.71, "comment": "Request executed", "request_id": 868062806, "retcode_external": 0, "request": [1, 234000, 0, "XAUUSD", 0.01, 3119.55, 0.0, 3143.0, 3.0, 10, 1, 1, 0, 0, "Order sent from Python script", 0, 0]}}2025-04-02 15:14:082025-04-02 15:14:14

This is the input that python read from Telegram :

Trade with DD XAUUSD sell 3133 sl 3143 tp1 3128 tp2 3123 tp3 3118

But this is what is sent to Metatrader :

{"signal": "sell", "symbol": "XAUUSD", "price": 3133.0, "sl": 3143.0, "tp": [1.0, 2.0, 3.0]}

It's like it taking the tp1, tp2, tp3 instead of the value of the tp 3128, 3123, 3118

Point1

If we take this information:

Trade with DD XAUUSD sell 3133 sl 3143 tp1 3128 tp2 3123 tp3 3118

Here there the sl 3143, tp1 3128, tp2 3123, tp3 3118

I want to know if when the deal closes, it has touched ‘sl 3143 then you can say display : Closed by Stop Loss (Loss)

If it touched ‘tp1 3128, ’ then you can say : Closed by Take Profit (Win)

If i manually close it or anything else then you can say : Closed by other reason (e.g., manually)

By this i can know if the telegram channel Trade with DD is good (I continue with it) or bad (I stop with it)

if am not wrong it uses **history_deals_get**
https://www.mql5.com/en/docs/python_metatrader5/mt5historydealsget_py

Point2

I currently have 3 Metatrader acc :

**ACC1 :** Blorvax - - **Metatrader**

**ACC2 :** Dekuy - - **icmarkets**

**ACC3** : Falkeg - - **VTMarket**

i need a screen as you said to be able to add, delete or modify them

The parameters that i need to see on the screen are as follows:
Account Name, Server Name, login ID, Password

Then in Channels i can select which Telegram channel connect to which Metatrader Channel

e.g : Trade with DD - - Blorvax

BTCUSD Forex Signals - - Dekuy

Don't forget the buy and sell limit

you’ll see the sell limit and buy limit and modification of tp and SL

[https://github.com/Quantreo/MetaTrader-5-AUTOMATED-TRADING-using-Python/blob/main/07 Advanced order placement.ipynb](https://github.com/Quantreo/MetaTrader-5-AUTOMATED-TRADING-using-Python/blob/main/07%20Advanced%20order%20placement.ipynb)

