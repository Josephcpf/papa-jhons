import json
import boto3
from datetime import datetime

from src.shared.dynamodb import ORDERS_TABLE, HISTORY_TABLE

events = boto3.client("events")


def update_order_status(order_id, new_status, worker_id=None, role=None):

    timestamp = datetime.utcnow().isoformat()

    order_response = ORDERS_TABLE.get_item(
        Key={
            "tenant_id": "PAPAJOHNS",
            "order_id": order_id
        }
    )

    order = order_response.get("Item", {})
    source = order.get("source", "UNKNOWN")

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

    history_item = {
        "order_id": order_id,
        "event_time": timestamp,
        "status": new_status
    }

    if worker_id:
        history_item["worker_id"] = worker_id

    if role:
        history_item["role"] = role

    HISTORY_TABLE.put_item(Item=history_item)

    event_detail = {
        "orderId": order_id,
        "status": new_status,
        "source": source,
        "timestamp": timestamp
    }

    if worker_id:
        event_detail["workerId"] = worker_id

    if role:
        event_detail["role"] = role

    events.put_events(
        Entries=[
            {
                "Source": "orders.service",
                "DetailType": "OrderStatusChanged",
                "EventBusName": "PapaJohnsEventBus",
                "Detail": json.dumps(event_detail)
            }
        ]
    )
