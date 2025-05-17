import boto3
from datetime import datetime
import uuid

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb')
tableVariables = dynamodb.Table('algoPyhtonVariables') # for variables like broker fees
variablesKey = "partionKey2"

tableData = dynamodb.Table('algoPythonBinanceData') # for monitor data
dataKey = "partionKey"

def get_float_value(itemName, table, keyName):
    response = table.get_item(Key={keyName: itemName})
    return float(response['Item']['value'])
    
def set_float_value(itemName, value, table, keyName):
    table.put_item(Item={keyName: itemName, 'value': str(value)})

def set_brokerFee_value(newValue):
    set_float_value('brokerFee', newValue, tableVariables, variablesKey)

def get_brokerFee_value():
    return get_float_value('brokerFee', tableVariables, variablesKey)

def add_transaction(action, amount, trading_pair, price, strategy):
    # Generate a unique transaction ID
    transaction_id = str(uuid.uuid4())
    
    # Current date and time
    date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    amount = str(amount)
    price = str(price)

    # Put the new transaction into the DynamoDB table
    tableData.put_item(
        Item={
            dataKey : transaction_id,  # Partition Key
            'action': action,                  # buy or sell
            'amount': amount,                  
            'trading_pair': trading_pair,      
            'price': price,                   
            'strategy' : strategy,              
            'date': date                       
        }
    )



# examples
# set_float_value('brokerFee', 0.03, tableVariables, variablesKey)
# add_transaction("Buy", 1, "BTCUSDT", 2, "hammer")


