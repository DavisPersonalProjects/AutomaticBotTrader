from binance.client import Client
import pandas as pd
import boto3
import dynamoDBmanager as DBmanager

api_key = ''
api_secret = ''

client = Client(api_key, api_secret, testnet=True)

brokerFee = 0.005 #0.5%
#brokerShare = 0

def SellingOrder(tradingPair, amount):
    #amount = round(amount, 8)

    order = client.order_market_sell(
    symbol=tradingPair,
    quantity=amount,
    recvWindow=50000
    )

    #calculates the expected fee
    amount = float(amount)

    global brokerFee
    ticker = client.get_symbol_ticker(symbol=tradingPair)
    current_price = float(ticker['price'])
    feeExpenses = current_price * amount * brokerFee
    brokerShare = DBmanager.get_brokerFee_value()
    brokerShare = float(brokerShare)
    brokerShare += feeExpenses
    DBmanager.set_brokerFee_value(brokerShare)

    print("Sell Order:", order)

def BuyingOrder(tradingPair, amount):
    #amount = round(amount, 8)

    order = client.order_market_buy(
    symbol=tradingPair,
    quantity=amount,
    recvWindow=50000
    )

    #calculates the expected fee
    amount = float(amount)

    global brokerFee
    ticker = client.get_symbol_ticker(symbol=tradingPair)
    current_price = float(ticker['price'])
    feeExpenses = current_price * amount * brokerFee

    brokerShare = DBmanager.get_brokerFee_value()
    brokerShare = float(brokerShare)
    brokerShare += feeExpenses

    DBmanager.set_brokerFee_value(brokerShare)

    print("Buy Order:", order)

def fetch_historical_data(symbol, interval, num_candles):
    klines = client.get_klines(symbol=symbol, interval=interval, limit=num_candles)
    data = []
    for kline in klines:
        timestamp, open_price, high, low, close_price, volume, close_time, quote_asset_volume, number_of_trades, taker_buy_base_asset_volume, taker_buy_quote_asset_volume, ignore = kline
        data.append([timestamp, open_price, close_price, high, low])

    df = pd.DataFrame(data, columns=['timestamp', 'Open', 'Close', 'High', 'Low'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df[['Open', 'High', 'Low', 'Close']] = df[['Open', 'High', 'Low', 'Close']].astype(float)
    #df = df.iloc[::-1].reset_index(drop=True) if reverse is needed
    return df

#candleSticks patterns
def hammer(df, index, pair): #pair = BTCUSDT or other

    minAmountBtc = "0.0001" #about 6 dollars
    amountWeight = 100 #amount of money spent
    length = 4 #the length of a downturn or upturn
    sensitivity = 1.10 #index in % that allows how sensitive it is to detect the pattern
    closePrices = df.Close
    openPrices = df.Open
    closePrice = closePrices.iloc[index]
    totalPriceChange = df.High.iloc[index] - df.Low.iloc[index]
    patternDetected = False #if there is consecutive upturn or donwturn in the given radius/length
    turns = [] # upturn = true, downturn = false

    for i in range(length):
        if(closePrices.iloc[index-i] > openPrices.iloc[index-i]):
            turns.append(True)
        elif(closePrices.iloc[index-i] < openPrices.iloc[index-i]):
            turns.append(False)
    if(all(x == turns[0] for x in turns)): #checks if all elements are the same
        if(turns[0] == False): #downTurn
            if(df.Close.iloc[index] * sensitivity >= df.High.iloc[index]): #hammerPattern
                BuyingOrder(pair, minAmountBtc)
                DBmanager.add_transaction("buy", minAmountBtc, "BTCUSDT", closePrice, "hammer")
            elif(df.Open.iloc[index] / sensitivity <= df.Low.iloc[index]): #invertedHammerPattern
                BuyingOrder(pair, minAmountBtc)
                DBmanager.add_transaction("buy", minAmountBtc, "BTCUSDT", closePrice, "hammer")

def pinBar(df, index, pair):
    minAmountBtc = "0.0001" #about 6 dollars
    amountWeight = 1 #amount of money spent
    length = 4 #the length of a downturn or upturn
    sensitivity = 1.10 #index in % that allows how sensitive it is to detect the pattern
    closePrices = df.Close
    openPrices = df.Open
    closePrice = closePrices.iloc[index]
    openPrice = openPrices.iloc[index]
    totalPriceChange = df.High.iloc[index] - df.Low.iloc[index]
    highLowMidpoint = totalPriceChange/2
    patternDetected = False #if there is consecutive upturn or donwturn in the given radius/length
    turns = [] # upturn = true, downturn = false

    for i in range(length):
        if(closePrices.iloc[index-i] > openPrices.iloc[index-i]):
            turns.append(True)
        elif(closePrices.iloc[index-i] < openPrices.iloc[index-i]):
            turns.append(False)
    if(all(x == turns[0] for x in turns)): #checks if all elements are the same
        if(turns[0] == True): #upturn
            if(openPrice < highLowMidpoint and closePrice < highLowMidpoint and closePrice > df.Low.iloc[index]):
                SellingOrder(pair, minAmountBtc) # bearish pinbar
                DBmanager.add_transaction("sell", minAmountBtc, "BTCUSDT", closePrice, "pinBar")
        elif(turns[0] == False): #downturn
            if(openPrice > highLowMidpoint and closePrice > highLowMidpoint and closePrice < df.High.iloc[index]):
                BuyingOrder(pair, minAmountBtc) # bullish pinbar
                DBmanager.add_transaction("buy", minAmountBtc, "BTCUSDT", closePrice, "pinBar")


def engulfing(df, index, pair):
    minAmountBtc = "0.0001" #about 6 dollars
    amountWeight = 100 #amount of money spent
    length = 4 #the length of a downturn or upturn
    sensitivity = 1.10 #index in % that allows how sensitive it is to detect the pattern
    closePrices = df.Close
    openPrices = df.Open
    closePrice = closePrices.iloc[index]
    openPrice = openPrices.iloc[index]
    totalPriceChange = df.High.iloc[index] - df.Low.iloc[index]
    highLowMidpoint = totalPriceChange/2
    patternDetected = False #if there is consecutive upturn or donwturn in the given radius/length
    turns = [] # upturn = true, downturn = false
    for i in range(length):
        if(closePrices.iloc[index-i] > openPrices.iloc[index-i]):
            turns.append(True)
        elif(closePrices.iloc[index-i] < openPrices.iloc[index-i]):
            turns.append(False)
    if(all(x == turns[0] for x in turns)): #checks if all elements are the same
        if(turns[0] == True): #upturn
            if(openPrices.iloc[index-1] < closePrices.iloc[index-1] and closePrice < closePrices.iloc[index-1]):
                SellingOrder(pair, minAmountBtc) # bullish engulfing
                DBmanager.add_transaction("sell", minAmountBtc, "BTCUSDT", closePrice, "engulfing")
        elif(turns[0] == False): #downturn
            if(openPrices.iloc[index-1] > closePrices.iloc[index-1] and closePrice > openPrices.iloc[index-1]):
                BuyingOrder(pair, minAmountBtc) # bullish engulfing
                DBmanager.add_transaction("buy", minAmountBtc, "BTCUSDT", closePrice, "engulfing")

def multipleStrategies(df, index, pair):
    hammer(df, index, pair)
    pinBar(df, index, pair)
    engulfing(df, index, pair)

def executeTrade(symbol):
    interval = Client.KLINE_INTERVAL_15MINUTE
    num_candles = 10  # Number of previous candles to fetch
    historical_data = fetch_historical_data(symbol, interval, num_candles)
    multipleStrategies(historical_data, num_candles-1, symbol) #num_candles-1 takes the last price fetced

    
#def lambda_handler(event, context): #basically the main() function
#    executeTrade('BTCUSDT')



