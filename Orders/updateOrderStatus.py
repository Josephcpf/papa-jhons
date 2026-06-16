import json
from datetime import datetime

from src.shared.dynamodb import (
    ORDERS_TABLE,
    HISTORY_TABLE
)


def handler(event, context):

    order_id = event["pathParameters"]["orderId"]

    body = json.loads(event["body"])

    new_status = body["status"]

    ORDERS_TABLE.update_item(
        Key={
            "tenant_id": "PAPAJOHNS",
            "order_id": order_id
        },
        UpdateExpression="""
            SET #status = :status,
                updated_at = :updated_at
        """,
        ExpressionAttributeNames={
            "#status": "status"
        },
        ExpressionAttributeValues={
            ":status": new_status,
            ":updated_at": datetime.utcnow().isoformat()
        }
    )

    HISTORY_TABLE.put_item(
        Item={
            "order_id": order_id,
            "event_time": datetime.utcnow().isoformat(),
            "status": new_status
        }
    )

    return {
        "statusCode": 200,
        "body": json.dumps({
            "order_id": order_id,
            "status": new_status
        })
    }
