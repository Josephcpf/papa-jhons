# Papa Johns Serverless Order Management System

Proyecto final de Cloud Computing basado en una arquitectura **serverless**, **event-driven**, **multi-tenant** y preparada para integración **multicloud**. El sistema modela el flujo de pedidos de Papa Johns, desde la creación del pedido hasta la entrega final, usando servicios administrados de AWS.

---

## 1. Descripción general

Este proyecto implementa un sistema de gestión de pedidos para Papa Johns. El flujo principal permite:

1. Crear pedidos.
2. Consultar pedidos.
3. Actualizar estados.
4. Gestionar el flujo operativo de cocina, empaque y entrega.
5. Registrar historial de estados.
6. Visualizar un resumen en dashboard.
7. Notificar a una integración externa simulada de Rappi cuando el pedido proviene de dicha fuente.
8. Orquestar tareas humanas mediante AWS Step Functions usando el patrón `waitForTaskToken`.

La arquitectura está desplegada en AWS usando **Serverless Framework**.

---

## 2. Arquitectura general

El sistema usa los siguientes servicios:

* **API Gateway HTTP API**: expone endpoints REST.
* **AWS Lambda**: ejecuta la lógica de negocio.
* **DynamoDB**: almacena pedidos, historial, workers y task tokens.
* **EventBridge**: comunica eventos entre servicios.
* **Step Functions**: orquesta el flujo de atención del pedido.
* **CloudWatch Logs**: registra evidencias y logs de ejecución.
* **Serverless Framework**: despliega infraestructura y funciones Lambda.

Flujo general:

```text
POST /orders
    ↓
createOrder guarda el pedido en DynamoDB
    ↓
createOrder publica evento OrderCreated en EventBridge
    ↓
OrderCreatedRule inicia Step Functions
    ↓
Step Functions espera tareas humanas con waitForTaskToken
    ↓
Workers completan cocina, empaque y entrega con send_task_success
    ↓
Cada cambio de estado publica OrderStatusChanged
    ↓
NotifyRappiRule escucha OrderStatusChanged
    ↓
notifyRappi notifica si source = RAPPI
    ↓
Dashboard consulta Orders y OrderHistory
```

---

## 3. Ambiente oficial desplegado

> Importante: este ambiente ya está desplegado y funcionando.
> No ejecutar `serverless deploy` sin coordinar con el equipo, porque podría modificar el stack oficial.

```text
AWS Account ID: 944585571319
Region: us-east-1
Service: josephcaba
Stage: dev
Runtime: Python 3.12
IAM Role: arn:aws:iam::944585571319:role/LabRole
```

Base URL:

```text
https://kz77grxdx4.execute-api.us-east-1.amazonaws.com
```

---

## 4. Estructura del proyecto

```text
papa-jhons/
│
├── serverless.yml
│
└── src/
    │
    ├── orders/
    │   ├── createOrder.py
    │   ├── getOrder.py
    │   ├── getOrderStatus.py
    │   └── updateOrderStatus.py
    │
    ├── workers/
    │   ├── saveTaskToken.py
    │   ├── startCooking.py
    │   ├── finishCooking.py
    │   ├── startPacking.py
    │   ├── finishPacking.py
    │   ├── startDelivery.py
    │   └── finishDelivery.py
    │
    ├── dashboard/
    │   └── getSummary.py
    │
    ├── notifications/
    │   └── notifyRappi.py
    │
    └── shared/
        ├── dynamodb.py
        └── order_utils.py
```

---

## 5. Recursos principales

### 5.1 Lambdas desplegadas

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

## 6. Endpoints disponibles

### Dashboard

```text
GET /dashboard/summary
```

### Orders

```text
POST /orders
GET /orders/{orderId}
GET /orders/{orderId}/status
PUT /orders/{orderId}/status
```

### Workers

```text
POST /workers/orders/{orderId}/start-cooking
POST /workers/orders/{orderId}/finish-cooking
POST /workers/orders/{orderId}/start-packing
POST /workers/orders/{orderId}/finish-packing
POST /workers/orders/{orderId}/start-delivery
POST /workers/orders/{orderId}/finish-delivery
```

---

## 7. Tablas DynamoDB

### 7.1 Orders

Tabla principal de pedidos.

```text
TableName: Orders
Partition Key: tenant_id
Sort Key: order_id
```

Ejemplo de item:

```json
{
  "tenant_id": "PAPAJOHNS",
  "order_id": "f6b9f61b-61fa-46ab-a1ff-1289c099777b",
  "customer_id": "CLIENT_WORKFLOW_001",
  "status": "CREATED",
  "source": "RAPPI",
  "total": 70.50,
  "created_at": "2026-06-19T04:18:00"
}
```

### 7.2 OrderHistory

Tabla que registra el historial de estados.

```text
TableName: OrderHistory
Partition Key: order_id
Sort Key: event_time
```

Ejemplo:

```json
{
  "order_id": "f6b9f61b-61fa-46ab-a1ff-1289c099777b",
  "event_time": "2026-06-19T04:20:08.277141",
  "status": "DELIVERED"
}
```

### 7.3 TaskTokens

Tabla usada por Step Functions para guardar los tokens del patrón `waitForTaskToken`.

```text
TableName: TaskTokens
Partition Key: order_id
```

Ejemplo:

```json
{
  "order_id": "TEST456",
  "task_token": "AQCAAAAAKgAAA..."
}
```

### 7.4 Workers

Tabla preparada para registrar trabajadores.

```text
TableName: Workers
Partition Key: worker_id
```

---

## 8. EventBridge

### Event Bus

```text
PapaJohnsEventBus
```

### Eventos principales

#### OrderCreated

Evento publicado cuando se crea un pedido.

```json
{
  "source": "orders.service",
  "detail-type": "OrderCreated",
  "detail": {
    "orderId": "f6b9f61b-61fa-46ab-a1ff-1289c099777b",
    "customerId": "CLIENT_WORKFLOW_001",
    "source": "RAPPI",
    "status": "CREATED",
    "timestamp": "2026-06-19T04:18:00"
  }
}
```

Este evento inicia el workflow de Step Functions.

#### OrderStatusChanged

Evento publicado cada vez que cambia el estado de un pedido.

```json
{
  "source": "orders.service",
  "detail-type": "OrderStatusChanged",
  "detail": {
    "orderId": "f6b9f61b-61fa-46ab-a1ff-1289c099777b",
    "status": "READY_FOR_DELIVERY",
    "source": "RAPPI",
    "timestamp": "2026-06-19T04:19:54.911749"
  }
}
```

Este evento activa la Lambda `notifyRappi`.

### Reglas configuradas

#### OrderCreatedRule

```text
Escucha: OrderCreated
Target: PapaJohnsOrderWorkflow
```

Sirve para iniciar automáticamente Step Functions cuando se crea un pedido.

#### NotifyRappiRule

```text
Escucha: OrderStatusChanged
Target: josephcaba-dev-notifyRappi
```

Sirve para notificar a Rappi cuando cambia el estado de un pedido que tiene `source = RAPPI`.

#### OrderStatusChangedRule

Esta regla fue desactivada para evitar que cada cambio de estado inicie una nueva ejecución de Step Functions.

```text
Estado recomendado: Disabled
```

---

## 9. Step Functions

### State Machine

```text
PapaJohnsOrderWorkflow
```

ARN:

```text
arn:aws:states:us-east-1:944585571319:stateMachine:PapaJohnsOrderWorkflow
```

### Flujo

```text
WaitCooking
    ↓
WaitPacking
    ↓
WaitDelivery
    ↓
Delivered
```

Cada etapa usa el patrón:

```text
arn:aws:states:::lambda:invoke.waitForTaskToken
```

Esto significa que Step Functions se queda esperando hasta que una Lambda externa le envíe un callback usando:

```python
send_task_success()
```

### Estados

#### WaitCooking

Espera a que el cocinero termine la preparación.

Se desbloquea con:

```text
POST /workers/orders/{orderId}/finish-cooking
```

#### WaitPacking

Espera a que el empaquetador termine el empaque.

Se desbloquea con:

```text
POST /workers/orders/{orderId}/finish-packing
```

#### WaitDelivery

Espera a que el repartidor entregue el pedido.

Se desbloquea con:

```text
POST /workers/orders/{orderId}/finish-delivery
```

#### Delivered

Estado final exitoso.

---

## 10. Integración simulada con Rappi

La Lambda `notifyRappi` simula una integración con una API externa de Rappi.

Actualmente no se llama a una API real. En su lugar, se registran logs en CloudWatch.

Ejemplo de log exitoso:

```text
Event received from EventBridge:
{
  "detail": {
    "orderId": "f6b9f61b-61fa-46ab-a1ff-1289c099777b",
    "status": "DELIVERED",
    "source": "RAPPI",
    "timestamp": "2026-06-19T04:20:08.277141"
  }
}

Sending notification to Rappi API for order f6b9f61b-61fa-46ab-a1ff-1289c099777b with status DELIVERED
```

En un escenario real, esta Lambda reemplazaría el `print()` por una llamada HTTP autenticada hacia la API oficial de Rappi.

Ejemplo conceptual:

```text
OrderStatusChanged
    ↓
EventBridge
    ↓
notifyRappi
    ↓
PUT https://api.rappi.com/orders/{orderId}/status
```

---

## 11. Requisitos para trabajar localmente

Cada integrante debe tener instalado:

```bash
node -v
npm -v
serverless --version
python3 --version
aws --version
```

Si Serverless no está instalado:

```bash
sudo npm install -g serverless
```

Si Serverless Framework V4 solicita login:

```bash
serverless login
```

---

## 12. Configuración de AWS CLI

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
aws_access_key_id=...
aws_secret_access_key=...
aws_session_token=...
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

Verificar acceso:

```bash
aws sts get-caller-identity
```

---

## 13. Instalación del proyecto

Clonar el repositorio:

```bash
git clone <URL_DEL_REPO>
cd papa-jhons
```

Verificar Serverless:

```bash
sls info
```

> Nota: si solo se quiere probar la demo, no es necesario hacer deploy.
> El ambiente oficial ya está desplegado.

---

## 14. Despliegue

Para desplegar todo:

```bash
serverless deploy
```

Para desplegar una función específica:

```bash
serverless deploy function -f createOrder
```

Ejemplos:

```bash
serverless deploy function -f updateOrderStatus
serverless deploy function -f finishCooking
serverless deploy function -f notifyRappi
```

> Importante: usar `serverless deploy` completo si se cambian archivos compartidos como `src/shared/order_utils.py`.

---

## 15. Comandos de prueba

### 15.1 Crear un pedido normal

```bash
curl -X POST \
"https://kz77grxdx4.execute-api.us-east-1.amazonaws.com/orders" \
-H "Content-Type: application/json" \
-d '{
  "customer_id": "CLIENT_TEST_001",
  "source": "WEB",
  "total": 45.90
}'
```

Respuesta esperada:

```json
{
  "order_id": "....",
  "status": "CREATED",
  "source": "WEB"
}
```

### 15.2 Crear un pedido Rappi

```bash
curl -X POST \
"https://kz77grxdx4.execute-api.us-east-1.amazonaws.com/orders" \
-H "Content-Type: application/json" \
-d '{
  "customer_id": "CLIENT_RAPPI_001",
  "source": "RAPPI",
  "total": 70.50
}'
```

Respuesta esperada:

```json
{
  "order_id": "....",
  "status": "CREATED",
  "source": "RAPPI"
}
```

Cuando se crea el pedido, EventBridge debe emitir `OrderCreated` y Step Functions debe iniciar automáticamente.

---

## 16. Completar flujo del pedido

Reemplazar `<ORDER_ID>` por el ID real del pedido.

### 16.1 Terminar cocina

```bash
curl -X POST \
"https://kz77grxdx4.execute-api.us-east-1.amazonaws.com/workers/orders/<ORDER_ID>/finish-cooking"
```

Respuesta esperada:

```json
{
  "order_id": "<ORDER_ID>",
  "status": "READY_FOR_PACKING",
  "message": "Cooking finished and workflow continued"
}
```

### 16.2 Terminar empaque

```bash
curl -X POST \
"https://kz77grxdx4.execute-api.us-east-1.amazonaws.com/workers/orders/<ORDER_ID>/finish-packing"
```

Respuesta esperada:

```json
{
  "order_id": "<ORDER_ID>",
  "status": "READY_FOR_DELIVERY",
  "message": "Packing finished and workflow continued"
}
```

### 16.3 Terminar entrega

```bash
curl -X POST \
"https://kz77grxdx4.execute-api.us-east-1.amazonaws.com/workers/orders/<ORDER_ID>/finish-delivery"
```

Respuesta esperada:

```json
{
  "order_id": "<ORDER_ID>",
  "status": "DELIVERED",
  "message": "Delivery finished and workflow completed"
}
```

---

## 17. Consultar pedido

### 17.1 Obtener pedido completo

```bash
curl -X GET \
"https://kz77grxdx4.execute-api.us-east-1.amazonaws.com/orders/<ORDER_ID>"
```

### 17.2 Obtener solo estado

```bash
curl -X GET \
"https://kz77grxdx4.execute-api.us-east-1.amazonaws.com/orders/<ORDER_ID>/status"
```

### 17.3 Actualizar estado manualmente

```bash
curl -X PUT \
"https://kz77grxdx4.execute-api.us-east-1.amazonaws.com/orders/<ORDER_ID>/status" \
-H "Content-Type: application/json" \
-d '{
  "status": "COOKING"
}'
```

---

## 18. Dashboard

Consultar resumen del sistema:

```bash
curl -X GET \
"https://kz77grxdx4.execute-api.us-east-1.amazonaws.com/dashboard/summary"
```

Respuesta ejemplo:

```json
{
  "total_orders": 4,
  "by_status": {
    "CREATED": 1,
    "READY_FOR_PACKING": 1,
    "DELIVERED": 2
  },
  "recent_history": [
    {
      "order_id": "TEST456",
      "status": "DELIVERED",
      "event_time": "2026-06-19T03:29:38.765342"
    }
  ]
}
```

---

## 19. Revisar logs

### Logs de notifyRappi

```bash
serverless logs -f notifyRappi --startTime 10m
```

### Logs de createOrder

```bash
serverless logs -f createOrder --startTime 10m
```

### Logs de updateOrderStatus

```bash
serverless logs -f updateOrderStatus --startTime 10m
```

### Logs de workers

```bash
serverless logs -f finishCooking --startTime 10m
serverless logs -f finishPacking --startTime 10m
serverless logs -f finishDelivery --startTime 10m
```

---

## 20. Consultas útiles de DynamoDB

### Ver historial de un pedido

```bash
aws dynamodb query \
--table-name OrderHistory \
--key-condition-expression "order_id = :id" \
--expression-attribute-values '{
  ":id":{"S":"<ORDER_ID>"}
}' \
--region us-east-1
```

### Ver tokens guardados

```bash
aws dynamodb scan \
--table-name TaskTokens \
--region us-east-1
```

### Ver pedido específico

```bash
aws dynamodb get-item \
--table-name Orders \
--key '{
  "tenant_id":{"S":"PAPAJOHNS"},
  "order_id":{"S":"<ORDER_ID>"}
}' \
--region us-east-1
```

---

## 21. Evidencias recomendadas para el informe

Capturas recomendadas:

1. `sls info` mostrando endpoints y funciones.
2. API Gateway con endpoints desplegados.
3. DynamoDB Tables: `Orders`, `OrderHistory`, `TaskTokens`, `Workers`.
4. Step Functions con ejecución completada.
5. Step Functions mostrando `WaitCooking`, `WaitPacking`, `WaitDelivery`, `Delivered`.
6. DynamoDB `OrderHistory` con estados del pedido.
7. Respuesta de `/dashboard/summary`.
8. Logs de `notifyRappi` mostrando eventos con `source = RAPPI`.
9. EventBridge rules:

   * `OrderCreatedRule`
   * `NotifyRappiRule`
10. CloudWatch logs de workers.

---

## 22. Caso de prueba exitoso

Pedido usado como evidencia:

```text
Order ID: f6b9f61b-61fa-46ab-a1ff-1289c099777b
Source: RAPPI
```

Estados notificados:

```text
READY_FOR_PACKING
READY_FOR_DELIVERY
DELIVERED
```

Logs confirmados:

```text
Sending notification to Rappi API for order f6b9f61b-61fa-46ab-a1ff-1289c099777b with status READY_FOR_PACKING
Sending notification to Rappi API for order f6b9f61b-61fa-46ab-a1ff-1289c099777b with status READY_FOR_DELIVERY
Sending notification to Rappi API for order f6b9f61b-61fa-46ab-a1ff-1289c099777b with status DELIVERED
```

---

## 23. Notas para el equipo

Para evitar errores:

```text
No ejecutar serverless deploy sin coordinar.
No eliminar reglas EventBridge.
No modificar Step Functions sin avisar.
No cambiar nombres de tablas DynamoDB.
No cambiar nombres de funciones Lambda.
```

El ambiente oficial ya está desplegado. Para la demo, usar los endpoints actuales.

---

## 24. Problemas comunes

### Error: Internal Server Error

Revisar logs:

```bash
serverless logs -f <functionName> --startTime 10m
```

### Error: Function not found en Step Functions

Verificar nombre real de Lambda:

```bash
aws lambda list-functions \
--query "Functions[*].FunctionName" \
--output table
```

### Error: Task token not found

Significa que se llamó a un endpoint `/finish-*` sin que Step Functions haya iniciado antes para ese pedido.

Solución:

1. Crear pedido con `POST /orders`.
2. Verificar que Step Functions está en `WaitCooking`.
3. Luego llamar a `/finish-cooking`.

### Error: Order is not from RAPPI

Significa que el evento llegó a `notifyRappi`, pero el pedido no tenía:

```text
source = RAPPI
```

Solo los pedidos con `source = RAPPI` generan notificación simulada.

---

## 25. Resumen técnico

El proyecto demuestra una arquitectura moderna basada en eventos:

```text
API Gateway
    ↓
Lambda
    ↓
DynamoDB
    ↓
EventBridge
    ↓
Step Functions
    ↓
Workers con callback
    ↓
EventBridge
    ↓
notifyRappi
```

Características implementadas:

```text
✓ Serverless
✓ Event-driven architecture
✓ Multi-tenancy básico mediante tenant_id
✓ Step Functions con waitForTaskToken
✓ Callback con send_task_success
✓ DynamoDB para persistencia
✓ Dashboard summary
✓ Integración externa simulada con Rappi
✓ Separación de microservicios por carpetas
```

---

## 26. Integrantes y responsabilidades

Completar según el grupo:

```text
Integrante 1: Arquitectura y backend serverless
Integrante 2: Frontend / Amplify
Integrante 3: Documentación / reporte
Integrante 4: Presentación / demo / evidencias
```

---

## 27. Estado del proyecto

```text
Backend principal: completado
Flujo Step Functions: completado
Dashboard: completado
Notificación Rappi simulada: completada
Evidencias: pendientes de adjuntar en informe/PPT
Frontend: pendiente o en desarrollo
```
