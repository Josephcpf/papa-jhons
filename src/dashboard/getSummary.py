import json
from decimal import Decimal
from src.shared.dynamodb import ORDERS_TABLE, HISTORY_TABLE


def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError


def handler(event, context):

    orders_response = ORDERS_TABLE.scan()
    orders = orders_response.get("Items", [])

    history_response = HISTORY_TABLE.scan()
    history = history_response.get("Items", [])

    by_status = {}

    for order in orders:
        status = order.get("status", "UNKNOWN")
        by_status[status] = by_status.get(status, 0) + 1

    recent_history = sorted(
        history,
        key=lambda x: x.get("event_time", ""),
        reverse=True
    )[:10]

    response = {
        "total_orders": len(orders),
        "by_status": by_status,
        "recent_history": recent_history
    }

    return {
        "statusCode": 200,
        "body": json.dumps(response, default=decimal_default)
    }
