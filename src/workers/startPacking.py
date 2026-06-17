import json

from src.shared.dynamodb import ORDERS_TABLE


def handler(event, context):

    order_id = event["pathParameters"]["orderId"]

    ORDERS_TABLE.update_item(
        Key={
            "tenant_id": "PAPAJOHNS",
            "order_id": order_id
        },
        UpdateExpression="SET #status = :status",
        ExpressionAttributeNames={
            "#status": "status"
        },
        ExpressionAttributeValues={
            ":status": "PACKING"
        }
    )

    return {
        "statusCode": 200,
        "body": json.dumps({
            "order_id": order_id,
            "status": "PACKING"
        })
    }
