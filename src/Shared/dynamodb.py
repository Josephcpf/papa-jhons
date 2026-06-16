import boto3

dynamodb = boto3.resource("dynamodb")

ORDERS_TABLE = dynamodb.Table("Orders")
HISTORY_TABLE = dynamodb.Table("OrderHistory")
