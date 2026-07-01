import json
from datetime import datetime


def handler(event, context):
    print("Preparing drink")
    print(json.dumps(event))

    order_id = event.get("order_id")

    return {
        "order_id": order_id,
        "drink_prepared": True,
        "prepared_at": datetime.utcnow().isoformat()
    }
