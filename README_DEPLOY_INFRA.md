# README_DEPLOY_INFRA.md

# Guía para crear funciones, Step Functions y eventos EventBridge

Esta guía explica cómo recrear la parte de infraestructura del proyecto Papa Johns: funciones Lambda, tablas DynamoDB, Step Functions y reglas de EventBridge.

> Importante: si el ambiente oficial ya está desplegado, no ejecutar estos comandos sin coordinar con el equipo. Esta guía es para recrear el ambiente desde cero o entender cómo fue configurado.

---

## 1. Requisitos previos

Antes de empezar, verificar que estén instalados:

```bash
node -v
npm -v
python3 --version
aws --version
serverless --version
```

Si Serverless no está instalado:

```bash
sudo npm install -g serverless
```

Si Serverless Framework solicita login:

```bash
serverless login
```

---

## 2. Configurar credenciales AWS

Crear carpeta de configuración:

```bash
mkdir -p ~/.aws
```

Editar credenciales:

```bash
nano ~/.aws/credentials
```

Formato:

```ini
[default]
aws_access_key_id=TU_ACCESS_KEY
aws_secret_access_key=TU_SECRET_KEY
aws_session_token=TU_SESSION_TOKEN
```

Editar configuración:

```bash
nano ~/.aws/config
```

Formato:

```ini
[default]
region=us-east-1
output=json
```

Verificar identidad:

```bash
aws sts get-caller-identity
```

Resultado esperado:

```json
{
  "Account": "944585571319",
  "Arn": "...",
  "UserId": "..."
}
```

---

## 3. Clonar proyecto

```bash
git clone <URL_DEL_REPO>
cd papa-jhons
```

Verificar archivos:

```bash
ls
ls src
```

Estructura esperada:

```text
serverless.yml
src/
  orders/
  workers/
  dashboard/
  notifications/
  shared/
```

---

## 4. Crear funciones Lambda y tablas con Serverless

El archivo principal de despliegue es:

```text
serverless.yml
```

Este archivo debe contener las funciones:

```yaml
functions:
  saveTaskToken:
    handler: src/workers/saveTaskToken.handler

  getDashboardSummary:
    handler: src/dashboard/getSummary.handler
    events:
      - httpApi:
          path: /dashboard/summary
          method: get

  notifyRappi:
    handler: src/notifications/notifyRappi.handler

  createOrder:
    handler: src/orders/createOrder.handler
    events:
      - httpApi:
          path: /orders
          method: post

  getOrder:
    handler: src/orders/getOrder.handler
    events:
      - httpApi:
          path: /orders/{orderId}
          method: get

  getOrderStatus:
    handler: src/orders/getOrderStatus.handler
    events:
      - httpApi:
          path: /orders/{orderId}/status
          method: get

  updateOrderStatus:
    handler: src/orders/updateOrderStatus.handler
    events:
      - httpApi:
          path: /orders/{orderId}/status
          method: put

  startCooking:
    handler: src/workers/startCooking.handler
    events:
      - httpApi:
          path: /workers/orders/{orderId}/start-cooking
          method: post

  finishCooking:
    handler: src/workers/finishCooking.handler
    events:
      - httpApi:
          path: /workers/orders/{orderId}/finish-cooking
          method: post

  startPacking:
    handler: src/workers/startPacking.handler
    events:
      - httpApi:
          path: /workers/orders/{orderId}/start-packing
          method: post

  finishPacking:
    handler: src/workers/finishPacking.handler
    events:
      - httpApi:
          path: /workers/orders/{orderId}/finish-packing
          method: post

  startDelivery:
    handler: src/workers/startDelivery.handler
    events:
      - httpApi:
          path: /workers/orders/{orderId}/start-delivery
          method: post

  finishDelivery:
    handler: src/workers/finishDelivery.handler
    events:
      - httpApi:
          path: /workers/orders/{orderId}/finish-delivery
          method: post
```

También debe contener las tablas DynamoDB:

```yaml
resources:
  Resources:

    PapaJohnsEventBus:
      Type: AWS::Events::EventBus
      Properties:
        Name: PapaJohnsEventBus

    OrdersTable:
      Type: AWS::DynamoDB::Table
      Properties:
        TableName: Orders
        BillingMode: PAY_PER_REQUEST
        AttributeDefinitions:
          - AttributeName: tenant_id
            AttributeType: S
          - AttributeName: order_id
            AttributeType: S
        KeySchema:
          - AttributeName: tenant_id
            KeyType: HASH
          - AttributeName: order_id
            KeyType: RANGE

    OrderHistoryTable:
      Type: AWS::DynamoDB::Table
      Properties:
        TableName: OrderHistory
        BillingMode: PAY_PER_REQUEST
        AttributeDefinitions:
          - AttributeName: order_id
            AttributeType: S
          - AttributeName: event_time
            AttributeType: S
        KeySchema:
          - AttributeName: order_id
            KeyType: HASH
          - AttributeName: event_time
            KeyType: RANGE

    WorkersTable:
      Type: AWS::DynamoDB::Table
      Properties:
        TableName: Workers
        BillingMode: PAY_PER_REQUEST
        AttributeDefinitions:
          - AttributeName: worker_id
            AttributeType: S
        KeySchema:
          - AttributeName: worker_id
            KeyType: HASH

    TaskTokensTable:
      Type: AWS::DynamoDB::Table
      Properties:
        TableName: TaskTokens
        BillingMode: PAY_PER_REQUEST
        AttributeDefinitions:
          - AttributeName: order_id
            AttributeType: S
        KeySchema:
          - AttributeName: order_id
            KeyType: HASH
```

Desplegar:

```bash
serverless deploy
```

Verificar:

```bash
sls info
```

Debe mostrar funciones como:

```text
saveTaskToken: josephcaba-dev-saveTaskToken
getDashboardSummary: josephcaba-dev-getDashboardSummary
notifyRappi: josephcaba-dev-notifyRappi
createOrder: josephcaba-dev-createOrder
...
```

---

## 5. Verificar funciones Lambda

Listar Lambdas del proyecto:

```bash
aws lambda list-functions \
--query "Functions[?contains(FunctionName,'josephcaba-dev')].FunctionName" \
--output table \
--region us-east-1
```

Resultado esperado:

```text
josephcaba-dev-saveTaskToken
josephcaba-dev-getDashboardSummary
josephcaba-dev-notifyRappi
josephcaba-dev-createOrder
josephcaba-dev-getOrder
josephcaba-dev-getOrderStatus
josephcaba-dev-updateOrderStatus
josephcaba-dev-startCooking
josephcaba-dev-finishCooking
josephcaba-dev-startPacking
josephcaba-dev-finishPacking
josephcaba-dev-startDelivery
josephcaba-dev-finishDelivery
```

---

## 6. Crear Step Functions

La máquina de estados debe llamarse:

```text
PapaJohnsOrderWorkflow
```

ARN esperado:

```text
arn:aws:states:us-east-1:944585571319:stateMachine:PapaJohnsOrderWorkflow
```

### Opción A: Crear desde consola AWS

Ir a:

```text
AWS Console
→ Step Functions
→ State machines
→ Create state machine
→ Write your workflow in code
```

Seleccionar:

```text
Type: Standard
Name: PapaJohnsOrderWorkflow
Role: LabRole
```

Pegar la definición:

```json
{
  "Comment": "Papa Johns Order Workflow with Wait for Callback",
  "StartAt": "WaitCooking",
  "States": {
    "WaitCooking": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke.waitForTaskToken",
      "Parameters": {
        "FunctionName": "josephcaba-dev-saveTaskToken",
        "Payload": {
          "order_id.$": "$.order_id",
          "taskToken.$": "$$.Task.Token"
        }
      },
      "Next": "WaitPacking"
    },
    "WaitPacking": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke.waitForTaskToken",
      "Parameters": {
        "FunctionName": "josephcaba-dev-saveTaskToken",
        "Payload": {
          "order_id.$": "$.order_id",
          "taskToken.$": "$$.Task.Token"
        }
      },
      "Next": "WaitDelivery"
    },
    "WaitDelivery": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke.waitForTaskToken",
      "Parameters": {
        "FunctionName": "josephcaba-dev-saveTaskToken",
        "Payload": {
          "order_id.$": "$.order_id",
          "taskToken.$": "$$.Task.Token"
        }
      },
      "Next": "Delivered"
    },
    "Delivered": {
      "Type": "Succeed"
    }
  }
}
```

---

## 7. Crear Step Functions por CLI

Crear archivo:

```bash
nano workflow.json
```

Pegar:

```json
{
  "Comment": "Papa Johns Order Workflow with Wait for Callback",
  "StartAt": "WaitCooking",
  "States": {
    "WaitCooking": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke.waitForTaskToken",
      "Parameters": {
        "FunctionName": "josephcaba-dev-saveTaskToken",
        "Payload": {
          "order_id.$": "$.order_id",
          "taskToken.$": "$$.Task.Token"
        }
      },
      "Next": "WaitPacking"
    },
    "WaitPacking": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke.waitForTaskToken",
      "Parameters": {
        "FunctionName": "josephcaba-dev-saveTaskToken",
        "Payload": {
          "order_id.$": "$.order_id",
          "taskToken.$": "$$.Task.Token"
        }
      },
      "Next": "WaitDelivery"
    },
    "WaitDelivery": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke.waitForTaskToken",
      "Parameters": {
        "FunctionName": "josephcaba-dev-saveTaskToken",
        "Payload": {
          "order_id.$": "$.order_id",
          "taskToken.$": "$$.Task.Token"
        }
      },
      "Next": "Delivered"
    },
    "Delivered": {
      "Type": "Succeed"
    }
  }
}
```

Crear la máquina:

```bash
aws stepfunctions create-state-machine \
--name PapaJohnsOrderWorkflow \
--definition file://workflow.json \
--role-arn arn:aws:iam::944585571319:role/LabRole \
--type STANDARD \
--region us-east-1
```

Si ya existe, actualizarla:

```bash
aws stepfunctions update-state-machine \
--state-machine-arn arn:aws:states:us-east-1:944585571319:stateMachine:PapaJohnsOrderWorkflow \
--definition file://workflow.json \
--region us-east-1
```

Verificar:

```bash
aws stepfunctions list-state-machines \
--region us-east-1
```

---

## 8. Crear reglas de EventBridge

El proyecto usa el Event Bus:

```text
PapaJohnsEventBus
```

Verificar que existe:

```bash
aws events list-event-buses \
--region us-east-1
```

Debe aparecer:

```text
PapaJohnsEventBus
```

---

## 9. Crear regla OrderCreatedRule

Esta regla escucha eventos `OrderCreated` y arranca Step Functions.

```bash
aws events put-rule \
--name OrderCreatedRule \
--event-bus-name PapaJohnsEventBus \
--event-pattern '{
  "source": ["orders.service"],
  "detail-type": ["OrderCreated"]
}' \
--region us-east-1
```

Conectar regla con Step Functions:

```bash
aws events put-targets \
--rule OrderCreatedRule \
--event-bus-name PapaJohnsEventBus \
--targets '[
  {
    "Id": "StartPapaJohnsWorkflow",
    "Arn": "arn:aws:states:us-east-1:944585571319:stateMachine:PapaJohnsOrderWorkflow",
    "RoleArn": "arn:aws:iam::944585571319:role/LabRole",
    "InputTransformer": {
      "InputPathsMap": {
        "orderId": "$.detail.orderId"
      },
      "InputTemplate": "{\"order_id\":\"<orderId>\"}"
    }
  }
]' \
--region us-east-1
```

Resultado esperado:

```json
{
  "FailedEntryCount": 0,
  "FailedEntries": []
}
```

---

## 10. Crear regla NotifyRappiRule

Esta regla escucha eventos `OrderStatusChanged` y ejecuta la Lambda `notifyRappi`.

```bash
aws events put-rule \
--name NotifyRappiRule \
--event-bus-name PapaJohnsEventBus \
--event-pattern '{
  "source": ["orders.service"],
  "detail-type": ["OrderStatusChanged"]
}' \
--region us-east-1
```

Antes de conectar la Lambda, agregar permiso para que EventBridge pueda invocarla:

```bash
aws lambda add-permission \
--function-name josephcaba-dev-notifyRappi \
--statement-id AllowEventBridgeInvokeNotifyRappi \
--action lambda:InvokeFunction \
--principal events.amazonaws.com \
--source-arn arn:aws:events:us-east-1:944585571319:rule/PapaJohnsEventBus/NotifyRappiRule \
--region us-east-1
```

Si aparece este error:

```text
ResourceConflictException
```

significa que el permiso ya existe y se puede continuar.

Conectar regla con Lambda:

```bash
aws events put-targets \
--rule NotifyRappiRule \
--event-bus-name PapaJohnsEventBus \
--targets '[
  {
    "Id": "NotifyRappiTarget",
    "Arn": "arn:aws:lambda:us-east-1:944585571319:function:josephcaba-dev-notifyRappi"
  }
]' \
--region us-east-1
```

Resultado esperado:

```json
{
  "FailedEntryCount": 0,
  "FailedEntries": []
}
```

---

## 11. Desactivar regla antigua si existe

Si existe una regla llamada:

```text
OrderStatusChangedRule
```

y apunta a Step Functions, debe desactivarse para evitar que cada cambio de estado cree una nueva ejecución.

```bash
aws events disable-rule \
--name OrderStatusChangedRule \
--event-bus-name PapaJohnsEventBus \
--region us-east-1
```

Verificar reglas:

```bash
aws events list-rules \
--event-bus-name PapaJohnsEventBus \
--region us-east-1
```

Estado esperado:

```text
OrderCreatedRule: ENABLED
NotifyRappiRule: ENABLED
OrderStatusChangedRule: DISABLED, si existe
```

---

## 12. Probar evento OrderCreated manualmente

Enviar evento:

```bash
aws events put-events \
--entries '[
  {
    "Source": "orders.service",
    "DetailType": "OrderCreated",
    "EventBusName": "PapaJohnsEventBus",
    "Detail": "{\"orderId\":\"TEST_EVENT_001\",\"source\":\"RAPPI\",\"status\":\"CREATED\"}"
  }
]' \
--region us-east-1
```

Resultado esperado:

```json
{
  "FailedEntryCount": 0,
  "Entries": [
    {
      "EventId": "..."
    }
  ]
}
```

Luego revisar Step Functions:

```text
AWS Console
→ Step Functions
→ PapaJohnsOrderWorkflow
→ Executions
```

Debe aparecer una ejecución nueva en estado:

```text
Running
```

detenida en:

```text
WaitCooking
```

Verificar token guardado:

```bash
aws dynamodb scan \
--table-name TaskTokens \
--region us-east-1
```

Debe aparecer:

```json
{
  "order_id": {
    "S": "TEST_EVENT_001"
  },
  "task_token": {
    "S": "AQCAAAAA..."
  }
}
```

---

## 13. Probar NotifyRappi manualmente

Enviar evento:

```bash
aws events put-events \
--entries '[
  {
    "Source": "orders.service",
    "DetailType": "OrderStatusChanged",
    "EventBusName": "PapaJohnsEventBus",
    "Detail": "{\"orderId\":\"RAPPI_TEST_001\",\"status\":\"COOKING\",\"source\":\"RAPPI\"}"
  }
]' \
--region us-east-1
```

Revisar logs:

```bash
serverless logs -f notifyRappi --startTime 10m
```

Resultado esperado:

```text
Event received from EventBridge
Sending notification to Rappi API for order RAPPI_TEST_001 with status COOKING
```

---

## 14. Probar flujo completo real

Crear pedido RAPPI:

```bash
curl -X POST \
"https://kz77grxdx4.execute-api.us-east-1.amazonaws.com/orders" \
-H "Content-Type: application/json" \
-d '{
  "customer_id": "CLIENT_INFRA_TEST",
  "source": "RAPPI",
  "total": 70.50
}'
```

Copiar el `order_id`.

Verificar que Step Functions inició automáticamente:

```text
Step Functions → PapaJohnsOrderWorkflow → Executions
```

Debe estar en:

```text
WaitCooking
```

Completar cocina:

```bash
curl -X POST \
"https://kz77grxdx4.execute-api.us-east-1.amazonaws.com/workers/orders/<ORDER_ID>/finish-cooking"
```

Completar empaque:

```bash
curl -X POST \
"https://kz77grxdx4.execute-api.us-east-1.amazonaws.com/workers/orders/<ORDER_ID>/finish-packing"
```

Completar entrega:

```bash
curl -X POST \
"https://kz77grxdx4.execute-api.us-east-1.amazonaws.com/workers/orders/<ORDER_ID>/finish-delivery"
```

Revisar Step Functions:

```text
Execution status: Succeeded
```

Revisar logs de Rappi:

```bash
serverless logs -f notifyRappi --startTime 10m
```

Debe mostrar:

```text
Sending notification to Rappi API for order <ORDER_ID> with status READY_FOR_PACKING
Sending notification to Rappi API for order <ORDER_ID> with status READY_FOR_DELIVERY
Sending notification to Rappi API for order <ORDER_ID> with status DELIVERED
```

---

## 15. Verificar historial DynamoDB

```bash
aws dynamodb query \
--table-name OrderHistory \
--key-condition-expression "order_id = :id" \
--expression-attribute-values '{
  ":id":{"S":"<ORDER_ID>"}
}' \
--region us-east-1
```

Estados esperados:

```text
READY_FOR_PACKING
READY_FOR_DELIVERY
DELIVERED
```

---

## 16. Verificar dashboard

```bash
curl -X GET \
"https://kz77grxdx4.execute-api.us-east-1.amazonaws.com/dashboard/summary"
```

Debe mostrar el total de pedidos y los estados agrupados.

---

## 17. Comandos útiles de diagnóstico

Listar reglas:

```bash
aws events list-rules \
--event-bus-name PapaJohnsEventBus \
--region us-east-1
```

Ver targets de `OrderCreatedRule`:

```bash
aws events list-targets-by-rule \
--rule OrderCreatedRule \
--event-bus-name PapaJohnsEventBus \
--region us-east-1
```

Ver targets de `NotifyRappiRule`:

```bash
aws events list-targets-by-rule \
--rule NotifyRappiRule \
--event-bus-name PapaJohnsEventBus \
--region us-east-1
```

Listar Step Functions:

```bash
aws stepfunctions list-state-machines \
--region us-east-1
```

Listar ejecuciones:

```bash
aws stepfunctions list-executions \
--state-machine-arn arn:aws:states:us-east-1:944585571319:stateMachine:PapaJohnsOrderWorkflow \
--region us-east-1
```

Ver logs de una función:

```bash
serverless logs -f <functionName> --startTime 10m
```

Ejemplo:

```bash
serverless logs -f saveTaskToken --startTime 10m
serverless logs -f finishCooking --startTime 10m
serverless logs -f notifyRappi --startTime 10m
```

---

## 18. Errores comunes

### 18.1 Function not found en Step Functions

Error ejemplo:

```text
Function not found: arn:aws:lambda:us-east-1:944585571319:function:saveTaskToken
```

Causa:

Step Functions está usando un nombre incorrecto de Lambda.

Solución:

```bash
aws lambda list-functions \
--query "Functions[?contains(FunctionName,'saveTaskToken')].FunctionName"
```

Usar el nombre real:

```text
josephcaba-dev-saveTaskToken
```

---

### 18.2 Task token not found

Causa:

Se llamó a `/finish-cooking`, `/finish-packing` o `/finish-delivery` sin que Step Functions esté esperando para ese pedido.

Solución:

1. Crear pedido con `POST /orders`.
2. Verificar que Step Functions inició y está en `WaitCooking`.
3. Llamar a `/finish-cooking`.

---

### 18.3 notifyRappi no se ejecuta

Verificar que la regla existe:

```bash
aws events list-rules \
--event-bus-name PapaJohnsEventBus \
--region us-east-1
```

Verificar target:

```bash
aws events list-targets-by-rule \
--rule NotifyRappiRule \
--event-bus-name PapaJohnsEventBus \
--region us-east-1
```

Verificar permiso Lambda:

```bash
aws lambda get-policy \
--function-name josephcaba-dev-notifyRappi \
--region us-east-1
```

---

### 18.4 notifyRappi dice “Order is not from RAPPI”

Causa:

El evento no tiene:

```json
"source": "RAPPI"
```

Solución:

Verificar que el pedido fue creado con:

```json
{
  "source": "RAPPI"
}
```

y que `order_utils.py` publica el campo `source`.

---

### 18.5 Step Functions no inicia al crear pedido

Verificar:

```bash
aws events list-targets-by-rule \
--rule OrderCreatedRule \
--event-bus-name PapaJohnsEventBus \
--region us-east-1
```

Debe apuntar a:

```text
arn:aws:states:us-east-1:944585571319:stateMachine:PapaJohnsOrderWorkflow
```

También verificar que `createOrder.py` publique `OrderCreated`.

---

## 19. Resumen de infraestructura manual

Aunque Serverless crea Lambdas, endpoints, tablas y el Event Bus, los siguientes recursos pueden requerir configuración manual o por CLI:

```text
Step Functions:
- PapaJohnsOrderWorkflow

EventBridge Rules:
- OrderCreatedRule
- NotifyRappiRule

EventBridge Targets:
- OrderCreatedRule → PapaJohnsOrderWorkflow
- NotifyRappiRule → josephcaba-dev-notifyRappi

Lambda Permission:
- Permiso para que EventBridge invoque notifyRappi

Regla desactivada:
- OrderStatusChangedRule
```

---

## 20. Flujo final esperado

```text
POST /orders
    ↓
createOrder
    ↓
DynamoDB Orders
    ↓
EventBridge: OrderCreated
    ↓
OrderCreatedRule
    ↓
Step Functions: PapaJohnsOrderWorkflow
    ↓
WaitCooking
    ↓
finishCooking + send_task_success
    ↓
WaitPacking
    ↓
finishPacking + send_task_success
    ↓
WaitDelivery
    ↓
finishDelivery + send_task_success
    ↓
Delivered
    ↓
OrderStatusChanged
    ↓
NotifyRappiRule
    ↓
notifyRappi
```

---

## 21. Checklist final

Antes de considerar el ambiente listo, verificar:

```text
[ ] serverless deploy ejecutado correctamente
[ ] Lambdas josephcaba-dev-* creadas
[ ] Tablas DynamoDB creadas
[ ] PapaJohnsEventBus creado
[ ] PapaJohnsOrderWorkflow creado
[ ] OrderCreatedRule creada
[ ] OrderCreatedRule apunta a Step Functions
[ ] NotifyRappiRule creada
[ ] NotifyRappiRule apunta a notifyRappi
[ ] Permiso de EventBridge hacia notifyRappi agregado
[ ] OrderStatusChangedRule desactivada, si existe
[ ] POST /orders crea pedido
[ ] Step Functions inicia automáticamente
[ ] finish-cooking avanza workflow
[ ] finish-packing avanza workflow
[ ] finish-delivery termina workflow
[ ] notifyRappi recibe eventos RAPPI
[ ] dashboard/summary responde correctamente
```
