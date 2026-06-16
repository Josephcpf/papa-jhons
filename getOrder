import boto3

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("Orders")

def handler(event, context):

    order_id = event["pathParameters"]["id"]

    response = table.get_item(
        Key={
            "tenant_id": "PAPAJOHNS",
            "order_id": order_id
        }
    )

    return {
        "statusCode": 200,
        "body": response.get("Item", {})
    }
