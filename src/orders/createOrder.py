import json
import boto3
import uuid
from decimal import Decimal
from datetime import datetime

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("Orders")

events = boto3.client("events")


def handler(event, context):

    body = json.loads(event["body"])

    order_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().isoformat()

    has_drink = body.get("has_drink", False)
    has_appetizer = body.get("has_appetizer", False)
    items = body.get("items", [])

    item = {
        "tenant_id": "PAPAJOHNS",
        "order_id": order_id,
        "customer_id": body["customer_id"],
        "status": "CREATED",
        "source": body["source"],
        "total": Decimal(str(body["total"])),
        "has_drink": has_drink,
        "has_appetizer": has_appetizer,
        "items": items,
        "created_at": timestamp
    }

    table.put_item(Item=item)

    events.put_events(
        Entries=[
            {
                "Source": "orders.service",
                "DetailType": "OrderCreated",
                "EventBusName": "PapaJohnsEventBus",
                "Detail": json.dumps({
                    "orderId": order_id,
                    "customerId": body["customer_id"],
                    "source": body["source"],
                    "status": "CREATED",
                    "has_drink": has_drink,
                    "has_appetizer": has_appetizer,
                    "timestamp": timestamp
                })
            }
        ]
    )

    return {
        "statusCode": 201,
        "body": json.dumps({
            "order_id": order_id,
            "status": "CREATED",
            "source": body["source"],
            "has_drink": has_drink,
            "has_appetizer": has_appetizer
        })
    }
