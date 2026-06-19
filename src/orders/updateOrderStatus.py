import json

from src.shared.order_utils import update_order_status


def handler(event, context):

    order_id = event["pathParameters"]["orderId"]

    body = json.loads(event["body"])
    new_status = body["status"]

    update_order_status(
        order_id,
        new_status
    )

    return {
        "statusCode": 200,
        "body": json.dumps({
            "order_id": order_id,
            "status": new_status
        })
    }
