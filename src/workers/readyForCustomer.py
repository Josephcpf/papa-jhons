import json

from src.shared.order_utils import update_order_status


def handler(event, context):

    order_id = event.get("order_id")
    fulfillment_type = event.get("fulfillment_type", "PICKUP")

    if fulfillment_type == "DINE_IN":
        final_status = "READY_FOR_TABLE"
        message = "Order is ready for dine-in customer"
    else:
        final_status = "READY_FOR_PICKUP"
        message = "Order is ready for pickup"

    update_order_status(
        order_id,
        final_status,
        worker_id="SYSTEM",
        role="SYSTEM"
    )

    return {
        "order_id": order_id,
        "status": final_status,
        "fulfillment_type": fulfillment_type,
        "message": message
    }
