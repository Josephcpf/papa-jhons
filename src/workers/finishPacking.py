import json
import boto3

from src.shared.dynamodb import TASKTOKENS_TABLE
from src.shared.order_utils import update_order_status

stepfunctions = boto3.client("stepfunctions")


def handler(event, context):

    order_id = event["pathParameters"]["orderId"]

    body = {}
    if event.get("body"):
        body = json.loads(event["body"])

    worker_id = body.get("worker_id", "PACKER_001")

    response = TASKTOKENS_TABLE.get_item(
        Key={
            "order_id": order_id
        }
    )

    item = response.get("Item")

    if not item:
        return {
            "statusCode": 404,
            "body": json.dumps({
                "message": "Task token not found for this order"
            })
        }

    task_token = item["task_token"]

    update_order_status(
        order_id,
        "READY_FOR_DELIVERY",
        worker_id=worker_id,
        role="PACKER"
    )

    stepfunctions.send_task_success(
        taskToken=task_token,
        output=json.dumps({
            "order_id": order_id,
            "status": "READY_FOR_DELIVERY"
        })
    )

    return {
        "statusCode": 200,
        "body": json.dumps({
            "order_id": order_id,
            "status": "READY_FOR_DELIVERY",
            "worker_id": worker_id,
            "role": "PACKER",
            "message": "Packing finished and workflow continued"
        })
    }
