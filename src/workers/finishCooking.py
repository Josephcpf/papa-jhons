import json

from src.shared.order_utils import update_order_status


def handler(event, context):

    order_id = event["pathParameters"]["orderId"]

    update_order_status(
        order_id,
        "READY_FOR_PACKING"
    )

    return {
        "statusCode": 200,
        "body": json.dumps({
            "order_id": order_id,
            "status": "READY_FOR_PACKING"
        })
    }
