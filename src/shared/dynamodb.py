import boto3

dynamodb = boto3.resource("dynamodb")

ORDERS_TABLE = dynamodb.Table("Orders")
HISTORY_TABLE = dynamodb.Table("OrderHistory")
WORKERS_TABLE = dynamodb.Table("Workers")
TASKTOKENS_TABLE = dynamodb.Table("TaskTokens")
