# Kafka Streaming Platform - Architecture

## Overview

This document describes the architecture, design decisions, and implementation details of the Kafka Streaming Platform demo.

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Web UI Layer                         │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Flask Backend + WebSocket (Port 8080)             │    │
│  │  Real-time message visualization                   │    │
│  └────────────────┬───────────────────────────────────┘    │
└───────────────────┼────────────────────────────────────────┘
                    │
┌───────────────────▼────────────────────────────────────────┐
│                  Kafka Broker Layer                        │
│  ┌────────────────────────────────────────────────────┐   │
│  │  Apache Kafka 3.6 (Port 9092)                      │   │
│  │  • Message storage and distribution                │   │
│  │  • 3 Topics with multiple partitions               │   │
│  │  • High-throughput message delivery                │   │
│  └────────────┬───────────────────┬───────────────────┘   │
└───────────────┼───────────────────┼────────────────────────┘
                │                   │
      ┌─────────▼───────┐  ┌────────▼──────────┐
      │   Zookeeper     │  │  Schema Registry  │
      │   (Port 2181)   │  │   (Port 8081)     │
      │  Coordination   │  │  Schema Mgmt      │
      └─────────────────┘  └───────────────────┘
                │                   │
┌───────────────▼───────────────────▼────────────────────────┐
│                 Application Layer                          │
│  ┌─────────────────────────────────────────────────────┐  │
│  │              Producers (3)                          │  │
│  │  • Event Producer    (user events)                  │  │
│  │  • Log Producer      (application logs)             │  │
│  │  • Metrics Producer  (system metrics)               │  │
│  └─────────────────────────────────────────────────────┘  │
│  ┌─────────────────────────────────────────────────────┐  │
│  │              Consumers (3)                          │  │
│  │  • Analytics Consumer (processes events)            │  │
│  │  • Alert Consumer     (monitors logs)               │  │
│  │  • Logger Consumer    (tracks metrics)              │  │
│  └─────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────┘
```

### Component Details

#### 1. Zookeeper (Coordination Layer)

**Purpose**: Cluster coordination and metadata management

**Responsibilities**:
- Broker registration and discovery
- Leader election for partitions
- Configuration management
- Cluster state tracking

**Configuration**:
```yaml
ZOOKEEPER_CLIENT_PORT: 2181
ZOOKEEPER_TICK_TIME: 2000
```

**Health Check**: TCP connection to port 2181

#### 2. Kafka Broker (Message Layer)

**Purpose**: Core message broker for streaming data

**Responsibilities**:
- Message persistence and replication
- Partition management
- Topic creation and configuration
- Consumer group coordination
- Message delivery guarantees

**Configuration**:
```yaml
KAFKA_BROKER_ID: 1
KAFKA_ZOOKEEPER_CONNECT: 'zookeeper:2181'
KAFKA_ADVERTISED_LISTENERS: 
  - PLAINTEXT://kafka:29092 (internal)
  - PLAINTEXT_HOST://localhost:9092 (external)
KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
KAFKA_LOG_RETENTION_HOURS: 24
```

**Topics**:
1. `user-events` (3 partitions) - User activity events
2. `application-logs` (2 partitions) - Application log messages
3. `system-metrics` (4 partitions) - System performance metrics

**Health Check**: Kafka broker API versions check

#### 3. Schema Registry (Schema Layer)

**Purpose**: Schema management and compatibility

**Responsibilities**:
- Schema versioning
- Compatibility checking
- Avro schema storage
- Schema evolution support

**Configuration**:
```yaml
SCHEMA_REGISTRY_KAFKASTORE_BOOTSTRAP_SERVERS: 'kafka:29092'
SCHEMA_REGISTRY_LISTENERS: http://0.0.0.0:8081
```

**Health Check**: HTTP GET to port 8081

#### 4. Producers (Data Generation Layer)

##### Event Producer

**Purpose**: Simulate user activity events

**Events Generated**:
- Clicks, purchases, signups, logins
- Page views, searches, cart actions

**Key Features**:
- Realistic user behavior simulation
- Key-based partitioning (user_id)
- Gzip compression
- Configurable event rate

**Configuration**:
```python
acks='all'              # Wait for all replicas
retries=3               # Retry on failure
compression_type='gzip' # Compress messages
linger_ms=10           # Batch delay
batch_size=16384       # Batch size in bytes
```

##### Log Producer

**Purpose**: Simulate application logs from microservices

**Log Levels**:
- DEBUG (20%), INFO (50%), WARN (20%), ERROR (8%), FATAL (2%)

**Services Simulated**:
- api-gateway, user-service, order-service
- payment-service, inventory-service
- notification-service, auth-service

**Key Features**:
- Weighted random log generation
- Realistic log message templates
- Service-based partitioning
- Trace IDs for errors

##### Metrics Producer

**Purpose**: Simulate system metrics from multiple hosts

**Metrics Types**:
- CPU usage and core counts
- Memory usage and swap
- Disk usage and I/O
- Network throughput

**Hosts Simulated**:
- web-server-01, web-server-02, web-server-03
- app-server-01, app-server-02
- db-server-01, db-server-02
- cache-server-01, queue-server-01

**Key Features**:
- Time-series data with realistic trends
- Host-based partitioning
- Snappy compression (good for metrics)
- High-volume streaming

#### 5. Consumers (Data Processing Layer)

##### Analytics Consumer

**Purpose**: Process user events for analytics

**Processing**:
- Event type classification
- User behavior tracking
- Statistics aggregation
- Purchase tracking

**Consumer Group**: `analytics-group`

**Key Features**:
- Auto-commit enabled (5s interval)
- Batch processing (100 records)
- Real-time statistics
- Event correlation

##### Alert Consumer

**Purpose**: Monitor logs and trigger alerts

**Processing**:
- Error detection and counting
- Warning monitoring
- Service health tracking
- Alert threshold management

**Consumer Group**: `alert-group`

**Key Features**:
- Error counting with time windows
- Configurable alert thresholds
- Service-level aggregation
- Real-time alerting

##### Logger Consumer

**Purpose**: Track metrics and detect anomalies

**Processing**:
- Metric type classification
- Anomaly detection (thresholds)
- Host-level monitoring
- Statistics tracking

**Consumer Group**: `logger-group`

**Key Features**:
- High-volume processing (500 records)
- Threshold-based alerts
- Metric aggregation
- Real-time monitoring

#### 6. Web UI (Visualization Layer)

**Purpose**: Real-time visualization and monitoring

**Technology Stack**:
- Backend: Flask (Python)
- Frontend: Vanilla JavaScript, HTML5, CSS3
- Real-time: Polling (2s interval)

**Features**:
- Topic overview and statistics
- Live message streams
- Consumer group monitoring
- Message search and filtering
- Real-time dashboards

**API Endpoints**:
- `/api/topics` - List all topics with stats
- `/api/messages/<topic>` - Get messages from topic
- `/api/stats` - Overall platform statistics
- `/api/latest/<topic>` - Latest message from topic
- `/health` - Health check

## Design Decisions

### 1. Single Broker vs. Cluster

**Decision**: Single broker for demo

**Rationale**:
- Simplifies deployment on Docker Desktop
- Reduces resource requirements
- Sufficient for learning concepts
- Production would use 3+ brokers

**Trade-offs**:
- No real replication
- Single point of failure
- Can't demonstrate broker failover
- Limited by single machine resources

### 2. Topic Partitioning Strategy

**user-events**: 3 partitions
- Moderate volume
- User-based partitioning (same user → same partition)
- Enables ordered event processing per user

**application-logs**: 2 partitions
- Lower volume
- Service-based partitioning
- Balanced log distribution

**system-metrics**: 4 partitions
- High volume
- Host-based partitioning
- Maximum parallelism for processing

### 3. Message Serialization

**Decision**: JSON with built-in serializers

**Rationale**:
- Human-readable for learning
- Easy to debug and inspect
- Native Python support
- No schema compilation needed

**Production Alternative**:
- Use Avro with Schema Registry
- Better performance
- Schema evolution support
- Smaller message sizes

### 4. Consumer Group Design

**Decision**: Separate consumer group per use case

**Rationale**:
- Each group gets all messages independently
- Demonstrates different processing patterns
- Shows consumer group isolation
- Enables multiple processing pipelines

### 5. Retention Policy

**Decision**: 24-hour retention, 1GB limit

**Rationale**:
- Sufficient for demo duration
- Prevents disk filling
- Realistic for development
- Easy to adjust for production

### 6. Compression Strategy

**Event Producer**: Gzip
- Good general-purpose compression
- Balanced CPU vs. size reduction

**Log Producer**: Gzip
- Text logs compress well
- Reduces network bandwidth

**Metrics Producer**: Snappy
- Fast compression/decompression
- Good for high-volume numeric data
- Lower CPU overhead

### 7. Producer Acknowledgments

**Event Producer**: `acks='all'`
- Highest reliability
- Wait for all replicas (in-sync replicas)
- Prevents data loss
- Slight latency increase

**Log/Metrics Producers**: `acks=1`
- Wait for leader only
- Faster, acceptable for logs/metrics
- Minor risk of loss on broker failure

### 8. Web UI Update Strategy

**Decision**: Polling with 2-second interval

**Rationale**:
- Simple to implement
- No WebSocket complexity
- Sufficient for demo
- Easy to understand

**Production Alternative**:
- WebSocket for true real-time
- Server-sent events (SSE)
- Kafka Streams integration

## Data Flow Patterns

### 1. Event Sourcing (user-events)

```
User Action → Event Producer → Kafka Topic → Analytics Consumer → Processed Events
                                     ↓
                              (Durable Log)
                                     ↓
                              Can Replay Anytime
```

**Benefits**:
- Complete audit trail
- Time-travel queries
- Replay for debugging
- Multiple consumers

### 2. Log Aggregation (application-logs)

```
Multiple Services → Log Producer → Kafka Topic → Alert Consumer → Alerts
                                          ↓
                                  (Centralized Store)
                                          ↓
                                   Search & Analysis
```

**Benefits**:
- Centralized logging
- Real-time alerting
- Historical analysis
- Correlation across services

### 3. Metrics Collection (system-metrics)

```
Multiple Hosts → Metrics Producer → Kafka Topic → Logger Consumer → Anomaly Detection
                                           ↓
                                   (Time-Series Data)
                                           ↓
                                    Dashboards & Alerts
```

**Benefits**:
- Real-time monitoring
- Anomaly detection
- Historical trending
- Capacity planning

## Scaling Considerations

### Horizontal Scaling

**Producers**: Stateless, scale easily
```bash
docker-compose up -d --scale event-producer=3
```

**Consumers**: Limited by partition count
- Max consumers per group = partition count
- user-events: Max 3 consumers
- application-logs: Max 2 consumers
- system-metrics: Max 4 consumers

**Kafka Brokers**: Add more brokers for production
- Distribute partition leadership
- Enable replication (RF=3 recommended)
- Better throughput and availability

### Vertical Scaling

**Kafka Broker**:
- Increase memory for page cache
- Add CPU cores for compression/encryption
- Fast SSD for disk I/O

**Producers/Consumers**:
- Increase batch sizes
- Tune buffer sizes
- Adjust thread counts

## Performance Characteristics

### Expected Throughput

**Event Producer**: ~0.5 msg/sec (configurable)
**Log Producer**: ~0.3 msg/sec (configurable)
**Metrics Producer**: ~1.8 msg/sec (9 hosts × 4 metrics / 20s)

**Total**: ~2.6 messages/sec (suitable for demo)

**Production**: Kafka can handle millions of messages/sec

### Latency

**End-to-End**: < 100ms typical
- Producer → Broker: ~10ms
- Broker → Consumer: ~10ms
- Processing: varies by consumer

**Network Latency**: Minimal (all containers on same host)

### Resource Usage

**Memory**: ~2-3 GB total
- Kafka: ~1 GB
- Producers/Consumers: ~200 MB each
- Web UI: ~100 MB

**CPU**: Low utilization
- Kafka: < 10% single core
- Producers/Consumers: < 5% each

**Disk**: Minimal
- Log data: < 1 GB/day
- Retained for 24 hours

## Monitoring and Observability

### Health Checks

All services have health checks:
- Zookeeper: TCP port check
- Kafka: Broker API check
- Schema Registry: HTTP endpoint
- Web UI: HTTP health endpoint

### Metrics Available

**Kafka Broker**:
- Message rate (in/out)
- Byte rate (in/out)
- Request metrics
- Partition counts

**Consumer Groups**:
- Lag per partition
- Commit offsets
- Member assignments

**Topics**:
- Message counts
- Partition distribution
- Retention status

### Logging

All components log to stdout:
```bash
docker-compose logs -f [service-name]
```

Logs include:
- Message processing
- Errors and warnings
- Performance metrics
- Consumer rebalancing

## Security Considerations

### Current (Demo)

- No authentication
- No encryption
- No authorization
- Suitable for local development only

### Production Recommendations

**Authentication**:
- SASL/SCRAM or SASL/PLAIN
- Mutual TLS (mTLS)
- Integration with LDAP/AD

**Encryption**:
- TLS for broker communication
- TLS for client connections
- Encryption at rest

**Authorization**:
- ACLs for topic access
- User/group permissions
- Schema Registry auth

**Network**:
- Firewall rules
- VPC isolation
- Private subnets

## Future Enhancements

### Potential Additions

1. **Kafka Connect**
   - Source connectors (databases, files)
   - Sink connectors (databases, S3)

2. **Kafka Streams**
   - Stream processing
   - Real-time transformations
   - Aggregations and joins

3. **ksqlDB**
   - SQL queries on streams
   - Materialized views
   - Real-time ETL

4. **Schema Evolution**
   - Avro schemas
   - Compatibility checking
   - Version management

5. **Monitoring Stack**
   - Prometheus for metrics
   - Grafana for dashboards
   - Kafka Manager UI

6. **Multi-Datacenter**
   - MirrorMaker 2
   - Active-active replication
   - Disaster recovery

## References

- [Apache Kafka Documentation](https://kafka.apache.org/documentation/)
- [Confluent Platform](https://docs.confluent.io/)
- [Kafka: The Definitive Guide](https://www.confluent.io/resources/kafka-the-definitive-guide/)
- [Designing Data-Intensive Applications](https://dataintensive.net/)

