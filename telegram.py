import MetaTrader5 as mt5
from pyrogram import Client, filters
import re
from time import sleep

from_chats = [
    {"id": 1882105856, "name": "CAC40 + FRA40 TRADING SIGNALS"},
    {"id": 1316632057, "name": "COMMITMENTS OF TRADER"},
    {"id": 1925709440, "name": "Forex Signal Factory (free)"},
    {"id": 1622798974, "name": "Forex US"},
    {"id": 1619062611, "name": "GBPUSD FX SIGNALS(firepips signal"},
    {"id": 2069311392, "name": "Gold Xpert"},
    {"id": 1986643106, "name": "ICT CHARTIST"},
    {"id": 1945187058, "name": "ICT OFFICIAL ACADEMY"},
    {"id": 1792592079, "name": "KR CAPITALS"},
    {"id": 1753932904, "name": "META TRADER 4&5 FOREX SIGNALS"},
    {"id": 1447871772, "name": "Market Makers FX"},
    {"id": 1240559594, "name": "Meta Trader 4 Signals (Free)"},
    {"id": 1924713375, "name": "Mr. Gold | Forex Signals (Free)"},
    {"id": 1972491378, "name": "NAS100 FOREX TRADING SIGNALS"},
    {"id": 1840185808, "name": "Smart Money Trader"},
    {"id": 1569743424, "name": "Snipers FX"},
    {"id": 1594662743, "name": "Trade with DD"},
    {"id": 1894282005, "name": "UKOIL + US30 SIGNAL"},
    {"id": 1898607875, "name": "US30 DOW JONES"},
    {"id": 1633769909, "name": "US30 Eagle"},
    {"id": 1253126344, "name": "US30 EMPIRE FREE FOREX SIGNALS"},
    {"id": 1206081401, "name": "VANTAGE FOREX SIGNALS OFFICIAL"},
    {"id": 1835439118, "name": "BTCUSD SIGNALS (FREE)"},
    {"id": 1967476990, "name": "FOXYICTRADER (P.G)"},
    {"id": 1983270625, "name": "BTCUSD FREE FOREX SIGNALS"},
    {"id": 1555470470, "name": "US30 KINGDOM"},
    {"id": 1799805861, "name": "Pro Forex System"},
    {"id": 2041761858, "name": "OKAKO (VIP)"},
    {"id": 1452557919, "name": "XAUUSD SIGNAL"}
]

symbols = ['AUDCAD', 'AUDCHF', 'AUDJPY', 'AUDNZD', 'AUDUSD', 'CADCHF', 'CADJPY', 'CHFJPY', 'GBPAUD', 'GBPCAD',
           'GBPCHF', 'GBPJPY', 'GBPNZD', 'GBPUSD', 'EURAUD', 'EURCAD', 'EURCHF', 'EURGBP', 'EURJPY', 'EURNZD',
           'EURUSD', 'NZDCAD', 'NZDCHF', 'NZDJPY', 'NZDUSD', 'USDCAD', 'USDCHF', 'USDCNH', 'USDJPY', 'XAUUSD']

bot = Client("name", api_id="", api_hash="")

def sltp(chat_id, text, Sl, Tp):
    try:
        PRICE = float(re.findall(r'[\d.]+', str(text.split('\n')[0]))[0])
        SL = float(re.findall(r'[\d.]+', str([i for i in text.split('\n') if Sl in i]))[-1])
        TP = float(re.findall(r'[\d.]+', str([i for i in text.split('\n') if Tp in i][-1]))[-1])
        return [PRICE, SL, TP]
    except:
        return False

def OrderSend(Symbol, Lot, Type, PRICE, Sl, Tp, Magic):
    selected = mt5.symbol_select(Symbol, True)
    if not selected:
        bot.send_message(-1001247941772, f"OrderSend.symbol_select: {str(mt5.last_error())}")
        mt5.shutdown()
    symbol_info = mt5.symbol_info(Symbol)
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": Symbol,
        "volume": Lot,
        "type": Type,
        "price": PRICE,
        "sl": Sl,
        "tp": Tp,
        "deviation": 3,
        "magic": Magic,
        "comment": "Order ochish",
        "type_time": mt5.ORDER_TIME_GTC,
    }
    result = mt5.order_send(request)
    mt5.shutdown()

@bot.on_message(filters.chat([chat['id'] for chat in from_chats]))
def my_handler(client, message):
    Type = 2
    NOW_PRICE = 0
    Lot = 0.01
    chat_id = message.chat.id
    text = str(message.text).lower()
    if message.photo:
        if message.caption:
            text = message.caption
    if chat_id < 0:
        if 0 < len(text):
            if not ('limit' in text) and not ('sell stop' in text) and not ('buy stop' in text):
                if ('sl' in text and 'tp' in text) or ('stop loss' in text and 'take profit' in text):
                    for Symbol in symbols:
                        if Symbol.lower() in text:
                            if 'buy' in text:
                                Type = 0
                            if 'sell' in text:
                                Type = 1
                            st = sltp(chat_id, text, 'sl', 'tp')
                            if st is not False and Type != 2:
                                for i in range(20):
                                    if mt5.initialize(login=68025724, server="RoboForex-DemoPro",
                                                      password="Metatrader5"):
                                        if abs(st[0] - NOW_PRICE) < 200 * mt5.symbol_info(Symbol).point:
                                            if Type == 0:
                                                NOW_PRICE = mt5.symbol_info_tick(Symbol).ask
                                            if Type == 1:
                                                NOW_PRICE = mt5.symbol_info_tick(Symbol).bid
                                            if mt5.symbol_info(Symbol) is not None:
                                                OrderSend(Symbol.upper(), Lot, Type, NOW_PRICE, st[1], st[2],
                                                          int(str(chat_id)[-10:]))
                                                break
                                            else:
                                                bot.send_message(-1001247941772,
                                                                 f"{str(mt5.last_error())}")
                                                OrderSend(Symbol.upper(), Lot, Type, NOW_PRICE, st[1], st[2],
                                                          int(str(chat_id)[-10:]))
                                                mt5.shutdown()
                                        else:
                                            mt5.shutdown()
                                            break
                                    sleep(5)

if __name__ == "__main__":
    bot.run()