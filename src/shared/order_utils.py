import json
import boto3
from datetime import datetime

from src.shared.dynamodb import (
    ORDERS_TABLE,
    HISTORY_TABLE
)

events = boto3.client("events")


def update_order_status(order_id, new_status):

    timestamp = datetime.utcnow().isoformat()

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
            ":updated_at": timestamp
        }
    )

    HISTORY_TABLE.put_item(
        Item={
            "order_id": order_id,
            "event_time": timestamp,
            "status": new_status
        }
    )

    events.put_events(
        Entries=[
            {
                "Source": "orders.service",
                "DetailType": "OrderStatusChanged",
                "EventBusName": "PapaJohnsEventBus",
                "Detail": json.dumps({
                    "orderId": order_id,
                    "status": new_status,
                    "timestamp": timestamp
                })
            }
        ]
    )
