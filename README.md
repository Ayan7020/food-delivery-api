# Real-Time Food Delivery System

A comprehensive microservices-based food delivery platform built with Python FastAPI, featuring real-time order processing, delivery tracking, and rating systems.

## 🏗️ System Architecture

This system follows a **microservices architecture** with event-driven communication patterns, ensuring scalability, maintainability, and fault tolerance.

#### **Important Note**: 
⚠️ **Always use the main `docker-compose.yml` file in the root directory to run the entire system.** 

**DO NOT** try to run individual services separately using their own docker-compose files, as this will require manual configuration of Redis, RabbitMQ, and database connections. The individual service docker-compose files are intended for production deployment scenarios only.

### Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Service  │    │Restaurant Service│   │Delivery Service │
│    (Port 8001)  │    │   (Port 8002)    │   │   (Port 8003)   │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
         ┌─────────────────────────────────────────────┐
         │           Message Broker Layer              │
         │  ┌─────────────┐    ┌─────────────────────┐ │
         │  │  RabbitMQ   │    │      Redis          │ │
         │  │(Port 5672)  │    │   (Port 6379)       │ │
         │  └─────────────┘    └─────────────────────┘ │
         └─────────────────────────────────────────────┘
                                 │
         ┌─────────────────────────────────────────────┐
         │            Database Layer                   │
         │ ┌─────────────┐ ┌─────────────┐ ┌─────────┐ │
         │ │PostgreSQL   │ │PostgreSQL   │ │PostgreSQL│ │
         │ │User DB      │ │Restaurant DB│ │Delivery │ │
         │ │(Port 5554)  │ │(Port 5555)  │ │DB 5556  │ │
         │ └─────────────┘ └─────────────┘ └─────────┘ │
         └─────────────────────────────────────────────┘
```

## 🧩 Microservices Breakdown

### 1. User Service (Port 8001)
**Responsibility**: User interactions, restaurant browsing, and rating management

**Key Features**:
- Restaurant catalog browsing
- User rating submission for orders and delivery agents
- User order history tracking

**Database Schema**:
- `userOrder`: Links users to their orders
- `userRating`: Stores ratings for orders and delivery agents

**API Endpoints**:
- `GET /restaurants` - Browse available restaurants
- `POST /ratings` - Submit ratings for orders/agents
- `GET /health` - Service health check

### 2. Restaurant Service (Port 8002)
**Responsibility**: Restaurant management, menu handling, and order processing

**Key Features**:
- Restaurant and menu item management
- Order processing and status updates
- Restaurant rating aggregation
- Real-time order queue consumption

**Database Schema**:
- `Restaurant`: Restaurant information and status
- `MenuItem`: Menu items with pricing
- `OrderGroup`: Groups orders from single user session
- `Order`: Individual restaurant orders
- `OrderItem`: Specific items within orders

**API Endpoints**:
- `GET /restaurants` - Restaurant management
- `POST /orders` - Order placement and management
- `GET /health` - Service health check

**Message Consumers**:
- `place-order-queue`: Processes incoming orders
- `ratings-exchange`: Updates restaurant ratings

### 3. Delivery Service (Port 8003)
**Responsibility**: Delivery agent management and order assignment

**Key Features**:
- Delivery agent registration and status management
- Automatic order assignment to available agents
- Delivery tracking and status updates
- Agent rating management

**Database Schema**:
- `DilveryAgent`: Agent information and availability status
- `DeliveryAssignment`: Order-to-agent assignments with delivery status

**API Endpoints**:
- `GET /agents` - Delivery agent management
- `GET /health` - Service health check

**Message Consumers**:
- `assign-dilvery-agent-queue`: Assigns orders to available agents
- `ratings-exchange`: Updates agent ratings

## 🔄 Event-Driven Communication

### Message Queues

**Direct Queues**:
1. **`place-order-queue`**: User → Restaurant Service
   - Triggers order creation and processing
   - Creates OrderGroup, Orders, and OrderItems

2. **`assign-dilvery-agent-queue`**: Restaurant → Delivery Service
   - Assigns confirmed orders to available delivery agents
   - Updates agent status to BUSY

**Fan-out Exchange**:
1. **`ratings-exchange`**: User Service → All Services
   - Broadcasts rating updates to relevant services
   - Updates restaurant and agent ratings across the system

### Message Flow

```
1. Order Placement:
   User Service → [place-order-queue] → Restaurant Service

2. Order Confirmation:
   Restaurant Service → [assign-dilvery-agent-queue] → Delivery Service

3. Rating Submission:
   User Service → [ratings-exchange] → Restaurant & Delivery Services
```

## 📡 Service Communication Diagram

### Complete Order Flow with Inter-Service Communication

```
┌─────────────────┐                    ┌─────────────────┐                    ┌─────────────────┐
│   User Service  │                    │Restaurant Service│                   │Delivery Service │
│   (Port 8001)   │                    │   (Port 8002)    │                   │   (Port 8003)   │
└─────────┬───────┘                    └─────────┬───────┘                    └─────────┬───────┘
          │                                      │                                      │
          │                                      │                                      │
          │ 1. Browse Restaurants                │                                      │
          │ GET /restaurants                     │                                      │
          │─────────────────────────────────────▶│                                      │
          │                                      │                                      │
          │ 2. Restaurant List Response          │                                      │
          │◀─────────────────────────────────────│                                      │
          │                                      │                                      │
          │ 3. Place Order Message               │                                      │
          │ [place-order-queue]                  │                                      │
          │─────────────────────────────────────▶│                                      │
          │                                      │                                      │
          │                                      │ 4. Process Order                     │
          │                                      │ - Create OrderGroup                  │
          │                                      │ - Create Orders                      │
          │                                      │ - Create OrderItems                  │
          │                                      │                                      │
          │                                      │ 5. Assign Delivery Agent            │
          │                                      │ [assign-dilvery-agent-queue]         │
          │                                      │─────────────────────────────────────▶│
          │                                      │                                      │
          │                                      │                                      │ 6. Find Available Agent
          │                                      │                                      │ - Query AVAILABLE agents
          │                                      │                                      │ - Create DeliveryAssignment
          │                                      │                                      │ - Update agent to BUSY
          │                                      │                                      │
          │ 7. Submit Rating                     │                                      │
          │ POST /ratings                        │                                      │
          │ (order_rating, agent_rating)         │                                      │
          │                                      │                                      │
          │ 8. Broadcast Rating Update           │                                      │
          │ [ratings-exchange] (FANOUT)          │                                      │
          │─────────────────────────────────────▶│                                      │
          │                      ┌───────────────┼──────────────────────────────────────┤
          │                      │               │                                      │
          │                      ▼               ▼                                      ▼
          │              ┌─────────────┐ ┌─────────────┐                      ┌─────────────┐
          │              │Update       │ │Update       │                      │Update Agent │
          │              │Restaurant   │ │Order Group  │                      │Rating       │
          │              │Rating       │ │Rating       │                      │             │
          │              └─────────────┘ └─────────────┘                      └─────────────┘
          │                                      │                                      │
          │                                      │ 9. Delivery Status Updates          │
          │                                      │ (PENDING → PICKED_UP → DELIVERED)   │
          │                                      │                                      │
          │                                      │                                      │ 10. Complete Delivery
          │                                      │                                      │ - Update status to DELIVERED
          │                                      │                                      │ - Set completedAt timestamp
          │                                      │                                      │ - Update agent to AVAILABLE
```

### Message Queue Architecture

```
                           ┌─────────────────────────────────────┐
                           │            RabbitMQ Broker          │
                           │              (Port 5672)            │
                           └─────────────────┬───────────────────┘
                                             │
            ┌────────────────────────────────┼────────────────────────────────┐
            │                                │                                │
    ┌───────▼───────┐                ┌──────▼──────┐                ┌────────▼────────┐
    │place-order-   │                │assign-      │                │ratings-exchange │
    │queue          │                │dilvery-     │                │(FANOUT)         │
    │               │                │agent-queue  │                │                 │
    │[Direct Queue] │                │[Direct Queue│                │[Fan-out Exchange│
    └───────┬───────┘                └──────┬──────┘                └────────┬────────┘
            │                               │                                │
            │                               │                                │
    ┌───────▼───────┐                ┌──────▼──────┐                ┌────────▼────────┐
    │User Service   │                │Delivery     │                │All Services     │
    │→ Restaurant   │                │Service      │                │(Restaurant &    │
    │Service        │                │             │                │Delivery)        │
    │               │                │Consumer:    │                │                 │
    │Consumer:      │                │assign_      │                │Consumers:       │
    │process_order  │                │dilvery_     │                │- process_order_ │
    │               │                │agent        │                │  rating         │
    │               │                │             │                │- process_dilvery│
    │               │                │             │                │  _rating        │
    └───────────────┘                └─────────────┘                └─────────────────┘
```

### Database Communication Pattern

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Service  │    │Restaurant Service│    │Delivery Service │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          │                      │                      │
          ▼                      ▼                      ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  PostgreSQL     │    │  PostgreSQL     │    │  PostgreSQL     │
│  User DB        │    │  Restaurant DB  │    │  Delivery DB    │
│  (Port 5554)    │    │  (Port 5555)    │    │  (Port 5556)    │
│                 │    │                 │    │                 │
│ Tables:         │    │ Tables:         │    │ Tables:         │
│ - userOrder     │    │ - Restaurant    │    │ - DilveryAgent  │
│ - userRating    │    │ - MenuItem      │    │ - Delivery      │
│                 │    │ - OrderGroup    │    │   Assignment    │
│                 │    │ - Order         │    │                 │
│                 │    │ - OrderItem     │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Real-Time Event Processing

```
Event Type: ORDER_PLACED
┌─────────────────┐
│   User Action   │ ──┐
│  (Place Order)  │   │
└─────────────────┘   │
                      ▼
            ┌─────────────────┐
            │  RabbitMQ       │
            │  place-order-   │
            │  queue          │
            └─────────┬───────┘
                      │
                      ▼
            ┌─────────────────┐
            │ Restaurant      │
            │ Service         │
            │ Consumer        │
            └─────────┬───────┘
                      │
          ┌───────────┼───────────┐
          ▼           ▼           ▼
    ┌─────────┐ ┌─────────┐ ┌─────────┐
    │Create   │ │Create   │ │Trigger  │
    │Order    │ │Order    │ │Delivery │
    │Group    │ │Items    │ │Assignment│
    └─────────┘ └─────────┘ └─────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  RabbitMQ       │
                    │  assign-        │
                    │  dilvery-agent- │
                    │  queue          │
                    └─────────┬───────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │ Delivery        │
                    │ Service         │
                    │ Consumer        │
                    └─────────────────┘

Event Type: RATING_SUBMITTED
┌─────────────────┐
│   User Action   │ ──┐
│ (Submit Rating) │   │
└─────────────────┘   │
                      ▼
            ┌─────────────────┐
            │  RabbitMQ       │
            │  ratings-       │
            │  exchange       │
            │  (FANOUT)       │
            └─────────┬───────┘
                      │
          ┌───────────┼───────────┐
          ▼           ▼           ▼
    ┌─────────┐ ┌─────────┐ ┌─────────┐
    │User     │ │Restaurant│ │Delivery │
    │Service  │ │Service   │ │Service  │
    │(Store)  │ │(Update   │ │(Update  │
    │         │ │Rating)   │ │Agent    │
    │         │ │          │ │Rating)  │
    └─────────┘ └─────────┘ └─────────┘
```

## 🗄️ Database Design

### Database Per Service Pattern
Each microservice maintains its own dedicated PostgreSQL database, ensuring:
- **Data isolation**: Services cannot directly access other services' data
- **Independent scaling**: Databases can be scaled based on service needs
- **Technology flexibility**: Each service can use different database technologies if needed

### Data Consistency
- **Eventual Consistency**: Updates propagate through message queues
- **Event Sourcing**: Rating updates broadcast to maintain consistency
- **Idempotency**: Message handlers designed to handle duplicate messages

## 🔧 Technology Stack

### Backend Framework
- **FastAPI**: High-performance Python web framework
- **Uvicorn**: ASGI server for FastAPI applications

### Database & ORM
- **PostgreSQL**: Primary database for all services
- **Prisma**: Type-safe database client and ORM
- **Redis**: Caching and session management

### Message Broker
- **RabbitMQ**: Reliable message queuing system
- **aio-pika**: Async Python client for RabbitMQ

### Infrastructure
- **Docker**: Containerization platform
- **Docker Compose**: Multi-container orchestration

## 🚀 Getting Started

### Prerequisites
- Docker and Docker Compose
- Python 3.11+

### 🐳 Docker Deployment (Recommended)



### Installation & Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd real-time-food-delivery-api
   ```

2. **Environment Configuration**
   Create `.env` files in each service directory:
   
   **user-service/.env**:
   ```
   DATABASE_URL="postgresql://postgres:password123@postgres_user:5432/user_service"
   RABBIT_MQ="amqp://guest:guest@rabbitmq:5672/"
   REDIS_URL="redis://redis:6379"
   ```
   
   **restaurant-service/.env**:
   ```
   DATABASE_URL="postgresql://postgres:password123@postgres_restaurant:5432/restaurant_service"
   RABBIT_MQ="amqp://guest:guest@rabbitmq:5672/"
   ```
   
   **delivery-service/.env**:
   ```
   DATABASE_URL="postgresql://postgres:password123@postgres_delivery:5432/delivery_service"
   RABBIT_MQ="amqp://guest:guest@rabbitmq:5672/"
   ```

3. **Start the Complete System**
   ```bash
   # Start all services, databases, and message brokers
   docker-compose up -d
   
   # Check if all services are running
   docker-compose ps
   
   # View logs for debugging (optional)
   docker-compose logs -f
   ```

4. **Database Migration** (If needed)
   ```bash
   # The system should auto-migrate on startup, but if manual migration is needed:
   docker-compose exec user_service npx prisma migrate dev
   docker-compose exec restaurant_service npx prisma migrate dev
   docker-compose exec delivery_service npx prisma migrate dev
   ```

### 🏗️ Docker Architecture

The system uses a multi-container Docker setup with the following structure:

```
├── docker-compose.yml              # Main orchestration file (USE THIS)
├── user-service/
│   ├── Dockerfile                  # User service container
│   └── docker-compose.yml          # Individual service (DEPLOYMENT ONLY)
├── restaurant-service/
│   ├── Dockerfile                  # Restaurant service container
│   └── docker-compose.yml          # Individual service (DEPLOYMENT ONLY)
└── delivery-service/
    ├── Dockerfile                  # Delivery service container
    └── docker-compose.yml          # Individual service (DEPLOYMENT ONLY)
```

### 🔄 Development vs Production

#### **Development (Local Testing)**
- **Use**: Main `docker-compose.yml` in root directory
- **Purpose**: Complete system with all dependencies
- **Command**: `docker-compose up -d`

#### **Production Deployment**
- **Use**: Individual service `docker-compose.yml` files
- **Purpose**: Independent service deployment
- **Requirements**: External Redis, RabbitMQ, and database configuration
- **Use Case**: Kubernetes, Docker Swarm, or separate cloud deployments

### Service URLs
- **User Service**: http://localhost:8001
- **Restaurant Service**: http://localhost:8002  
- **Delivery Service**: http://localhost:8003
- **RabbitMQ Management**: http://localhost:15672 (guest/guest)
- **Redis**: localhost:6379

## 📊 System Features

### Real-Time Processing
- **Asynchronous message handling** for order processing
- **Event-driven architecture** for real-time updates
- **Background task processing** for delivery assignments

### Scalability Features
- **Microservices architecture** for independent scaling
- **Database per service** pattern for data isolation
- **Message queuing** for handling high throughput
- **Redis caching** for improved performance

### Reliability & Resilience
- **Health checks** for all services and dependencies
- **Persistent message delivery** with RabbitMQ
- **Database connection pooling** with Prisma
- **Error handling** with custom exception handlers

### Data Integrity
- **ACID transactions** within each service
- **Event sourcing** for cross-service data consistency
- **Unique constraints** to prevent duplicate data
- **Cascading deletes** for referential integrity

## 🔍 Monitoring & Observability

### Health Checks
Each service exposes a `/health` endpoint for monitoring:
```bash
curl http://localhost:8001/health  # User Service
curl http://localhost:8002/health  # Restaurant Service  
curl http://localhost:8003/health  # Delivery Service
```

### Message Queue Monitoring
Access RabbitMQ Management UI at http://localhost:15672 to monitor:
- Queue depths and message rates
- Consumer connections and performance
- Exchange routing and binding status

## 🚦 System Status Flow

### Order Lifecycle
1. **Order Placement** → `PENDING`
2. **Restaurant Confirmation** → `CONFIRMED`
3. **Agent Assignment** → `PICKED_UP`
4. **Delivery Completion** → `DELIVERED`
5. **User Rating** → Rating stored and broadcasted

### Agent Status Flow
1. **Available** → Ready for assignments
2. **Busy** → Currently handling delivery
3. **Available** → Returns after delivery completion

## 🔐 Error Handling

### Custom Exception Handling
- **AppException**: Application-specific errors
- **UniqueViolationError**: Database constraint violations
- **RecordNotFoundError**: Missing database records
- **Internal Server Error**: Unexpected system errors

### Graceful Degradation
- Services continue operating even if dependent services are temporarily unavailable
- Message queuing ensures no data loss during service outages
- Circuit breaker patterns prevent cascade failures

## 🎯 Future Enhancements

### Potential Improvements
1. **API Gateway**: Centralized routing and authentication
2. **Service Discovery**: Dynamic service registration and discovery
3. **Distributed Tracing**: Request tracing across services
4. **Metrics Collection**: Prometheus/Grafana monitoring
5. **Load Balancing**: Multiple instance management
6. **Authentication & Authorization**: JWT-based security
7. **Notification Service**: Real-time user notifications
8. **Payment Service**: Integrated payment processing

### Scaling Considerations
- **Horizontal Scaling**: Multiple service instances
- **Database Sharding**: Partition data across multiple databases  
- **Message Queue Clustering**: RabbitMQ cluster setup
- **Caching Strategy**: Redis cluster for distributed caching

---

## 📝 Development Notes

This system demonstrates several important architectural patterns:
- **Microservices Architecture**
- **Event-Driven Communication**
- **Database Per Service**
- **CQRS (Command Query Responsibility Segregation)**
- **Eventually Consistent Data**

The codebase serves as a foundation for building production-ready food delivery platforms with room for extensive customization and scaling.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request 
