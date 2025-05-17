# AutomaticBotTrader
This project is an automated cryptocurrency trading bot deployed as an AWS Lambda function, designed to execute technical trading strategies using Binance's Testnet API. It employs AWS CloudWatch Events to trigger executions every 15 minutes, facilitating continuous market analysis and automated trades.

Features

Automated Trading: Executes buy and sell orders on Binance Testnet.

Technical Analysis: Detects and acts on candlestick patterns including Hammer, PinBar, and Engulfing.

Serverless Architecture: Utilizes AWS Lambda for scalable, event-driven execution.

Scheduled Operations: Automated execution every 15 minutes through AWS CloudWatch Events.

Persistent Data Storage: Stores transaction data and trading metrics securely using AWS DynamoDB.

Project Components

Lambda Execution

lambda_function.py: Entry point for AWS Lambda, initiating the trading logic.

Core Trading Logic

BinanceSpotTestnetPackage.py: Contains trading strategies, order management, and market data retrieval from Binance Testnet.

Data Management

dynamoDBmanager.py: Manages broker fees, transaction logs, and historical data persistence in AWS DynamoDB.

Trading Strategies Implemented

Hammer Pattern: Detects market reversals after downturns to initiate buy orders.

PinBar Pattern: Identifies price rejections at critical levels to trigger buys or sells.

Engulfing Pattern: Recognizes reversal signals from candlesticks to execute opposing trades.

Each strategy analyzes recent market data with adjustable sensitivity parameters to ensure timely and precise trade execution.

Technology Stack

Python

AWS Lambda

AWS CloudWatch Events

AWS DynamoDB

Binance Testnet API

Example Data Structure (DynamoDB)

Transaction record structure:

{
  "partionKey": "uuid-transaction-id",
  "action": "buy",
  "amount": "0.0001",
  "trading_pair": "BTCUSDT",
  "price": "65234.51",
  "strategy": "hammer",
  "date": "2025-05-17 18:30:00"
}
