import json


def handler(event, context):

    print("Event received from EventBridge:")
    print(json.dumps(event))

    detail = event.get("detail", {})

    order_id = detail.get("orderId") or detail.get("order_id")
    status = detail.get("status")
    source = detail.get("source", "UNKNOWN")

    if source != "RAPPI":
        print("Order is not from RAPPI. Notification skipped.")

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Notification skipped",
                "reason": "Order source is not RAPPI",
                "order_id": order_id,
                "status": status
            })
        }

    print(f"Sending notification to Rappi API for order {order_id} with status {status}")

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Rappi notification simulated",
            "order_id": order_id,
            "status": status
        })
    }
