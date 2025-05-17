import BinanceSpotTestnetPackage as algoScipt
import boto3


def lambda_handler(event, context): #basically the main() function
    algoScipt.executeTrade('BTCUSDT')

#algoScipt.executeTrade('BTCUSDT')

