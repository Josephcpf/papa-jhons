import json


def process_event(event):

    print("Event received:")
    print(json.dumps(event))

    detail = event.get("detail", {})

    order_id = detail.get("orderId") or detail.get("order_id")
    status = detail.get("status")
    source = detail.get("source", "UNKNOWN")
    timestamp = detail.get("timestamp")

    if source != "RAPPI":
        print("Order is not from RAPPI. Notification skipped.")
        return

    print(
        f"Sending notification to Rappi API for order {order_id} "
        f"with status {status} at {timestamp}"
    )


def handler(event, context):

    print("Raw event received:")
    print(json.dumps(event))

    if "Records" in event:
        for record in event["Records"]:
            body = json.loads(record["body"])
            process_event(body)
    else:
        process_event(event)

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Rappi notification processing completed"
        })
    }
