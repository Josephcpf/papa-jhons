import json

from src.shared.dynamodb import TASKTOKENS_TABLE


def handler(event, context):

    order_id = event["order_id"]
    task_token = event["taskToken"]

    TASKTOKENS_TABLE.put_item(
        Item={
            "order_id": order_id,
            "task_token": task_token
        }
    )

    return {
        "status": "saved"
    }
