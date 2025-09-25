# Third Party API Integration

Este proyecto implementa una arquitectura hexagonal con **FastAPI**, **MongoDB** y **RabbitMQ**, para sincronizar información de **clientes**, **empresas** y **facturas** con **Factura.com**.  

---

## 📌 Características principales
- Recepción de eventos desde RabbitMQ.
- Procesamiento de datos de **clientes** y **empresas**.
- Creación y sincronización automática con **Factura.com**.
- Persistencia en **MongoDB**.
- Arquitectura limpia con **casos de uso**, **repositorios**, **entidades** y **adaptadores externos**.
- Contenerización con **Docker Compose**.

---

## 📂 Arquitectura

```plaintext
app/
├── client/
│   ├── application/   # Casos de uso y DTOs
│   ├── domain/        # Entidades y repositorios
│   └── infrastructure # Controladores, adapters y repositorios Mongo
├── company/
│   ├── application/   
│   ├── domain/        
│   └── infrastructure
├── shared/
│   └── infrastructure/messaging # Consumer y handlers de eventos
├── config/            # Configuración de DB y settings
├── main.py            # Entry point FastAPI

```

### Flujo principal

`Evento recibido (RabbitMQ)      → Handler correspondiente (client/company/invoice)         → Caso de uso (ej. InvoiceClientUseCase)             → Validación / creación de cliente             → Conexión con Factura.com             → Guardar en MongoDB`

---

## 🧩 Eventos y Payloads

### 1️⃣ Cliente creado

```json
{   "tenant_id": "abc-123",   "rfc": "XAXX010101000",   "business_name": "Empresa Demo",   "tax_regime": "603",   "address": {     "street": "Av. Siempre Viva",     "exterior_number": "742",     "neighborhood": "Centro",     "zip_code": "06000",     "city": "CDMX",     "state": "Ciudad de México",     "country": "MEX"   },   "contact": {     "name": "Juan",     "last_names": "Pérez López",     "email": "juan.perez@mail.com",     "phone": "5555555555"   },   "cfdi_use": "G03" }
```

### 2️⃣ Empresa sincronizada

```json
{   "tenantId": "abc-123",   "businessName": "Mi Empresa SA de CV",   "tradeName": "Mi Empresa",   "fiscalData": {     "rfc": "AAA010101AAA",     "regime": "601"   },   "contact": {     "phone": "5512345678",     "website": "https://miempresa.com"   },   "emails": {     "billing": "facturacion@miempresa.com",     "support": "soporte@miempresa.com"   } }
```

### 3️⃣ Factura emitida


```json
{   "rfc": "AAA010101AAA",   "business_name": "Mi Empresa SA de CV",   "invoice_details": {     "folio": "F1234",     "total": 1500.50,     "currency": "MXN",     "items": [       { "description": "Servicio de consultoría", "quantity": 1, "unit_price": 1500.50 }     ]   } }
```

---

## 🗄️ Estructura de la base de datos (MongoDB)

### Colección `clients`

```json
{   "_id": "ObjectId",   "tenant_id": "abc-123",   "external_uid": "UID_FACTURA",   "rfc": "XAXX010101000",   "business_name": "Empresa Demo",   "tax_regime": "603",   "tax_regime_name": "Personas Morales con Fines no Lucrativos",   "address": { ... },   "contact": { ... },   "emails": ["juan.perez@mail.com"],   "cfdi_use": "G03",   "cfdi_use_name": "Gastos en general",   "created_at": "2025-01-01T12:00:00",   "updated_at": "2025-01-01T12:00:00",   "status": "active",   "factura_sync": true }
```

### Colección `companies`

```json
{   "_id": "ObjectId",   "tenant_id": "abc-123",   "business_name": "Mi Empresa SA de CV",   "trade_name": "Mi Empresa",   "fiscal_data": { "rfc": "AAA010101AAA", "regime": "601" },   "emails": { "billing": "facturacion@miempresa.com" },   "metadata": { ... } }
```

---

## ⚙️ Instalación y ejecución

### 1. Clonar repositorio

`git clone https://github.com/tu-repo/third-party-api.git cd third-party-api`

### 2. Crear archivo `.env`

`MONGO_USER=admin MONGO_PASS=secret RABBITMQ_USERNAME=guest RABBITMQ_PASSWORD=guest FACTURA_COM_API_KEY=tu_api_key FACTURA_COM_SECRET_KEY=tu_secret`

### 3. Levantar con Docker

`docker-compose up --build`

### 4. Acceder a servicios

- API → [http://localhost:8000](http://localhost:8000)
    
- RabbitMQ Management → [http://localhost:15672](http://localhost:15672)
    
- MongoDB → `localhost:27017`
    

---

## 📊 Flujo resumido

`Evento recibido (RabbitMQ)         ↓ Handler procesa payload         ↓ Caso de uso valida datos         ↓ Factura.com (sincronización)         ↓ Guardar en MongoDB`

---

## 📖 Tecnologías

- FastAPI
    
- [MongoDB](https://www.mongodb.com/)
    
- RabbitMQ
    
- Docker Compose
    
- [Factura.com API](https://factura.com/)