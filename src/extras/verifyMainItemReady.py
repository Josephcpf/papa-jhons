import json
from datetime import datetime


def handler(event, context):
    print("Verifying main item is ready")
    print(json.dumps(event))

    order_id = event.get("order_id")

    return {
        "order_id": order_id,
        "main_item_ready": True,
        "verified_at": datetime.utcnow().isoformat()
    }
