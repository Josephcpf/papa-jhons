import json

from src.shared.order_utils import update_order_status


def handler(event, context):

    order_id = event["pathParameters"]["orderId"]

    update_order_status(
        order_id,
        "PACKING"
    )

    return {
        "statusCode": 200,
        "body": json.dumps({
            "order_id": order_id,
            "status": "PACKING"
        })
    }
