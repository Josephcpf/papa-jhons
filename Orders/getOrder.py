import json

from src.shared.dynamodb import ORDERS_TABLE


def handler(event, context):

    order_id = event["pathParameters"]["orderId"]

    response = ORDERS_TABLE.get_item(
        Key={
            "tenant_id": "PAPAJOHNS",
            "order_id": order_id
        }
    )

    item = response.get("Item")

    if not item:
        return {
            "statusCode": 404,
            "body": json.dumps({
                "message": "Order not found"
            })
        }

    return {
        "statusCode": 200,
        "body": json.dumps(item)
    }
