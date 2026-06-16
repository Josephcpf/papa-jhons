import json
import boto3
import uuid
from datetime import datetime

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("Orders")

def handler(event, context):

    body = json.loads(event["body"])

    order_id = str(uuid.uuid4())

    item = {
        "tenant_id": "PAPAJOHNS",
        "order_id": order_id,
        "customer_id": body["customer_id"],
        "status": "CREATED",
        "source": body["source"],
        "total": body["total"],
        "created_at": datetime.utcnow().isoformat()
    }

    table.put_item(Item=item)

    return {
        "statusCode": 201,
        "body": json.dumps({
            "order_id": order_id,
            "status": "CREATED"
        })
    }
