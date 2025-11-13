# Kafka Streaming Platform Demo

A comprehensive demonstration of Apache Kafka streaming concepts featuring multiple producers, consumers, topics, and a real-time web UI for visualizing message flows. Perfect for learning Kafka fundamentals with Docker on macOS.

![Platform Status](https://img.shields.io/badge/status-ready-brightgreen)
![Docker](https://img.shields.io/badge/docker-required-blue)
![Kafka](https://img.shields.io/badge/kafka-3.6-orange)
![Python](https://img.shields.io/badge/python-3.11-green)

## Overview

This project demonstrates:
- **Apache Kafka** message broker and streaming platform
- **Multiple Topics** showcasing different messaging patterns
- **Producer & Consumer** services in Python
- **Real-time Web UI** for visualizing message flows
- **Stream Processing** with consumer groups
- **Kafka Architecture** with Zookeeper coordination
- **Message Patterns** including pub/sub, work queues, and event sourcing

## Architecture

The platform consists of 7 containerized services:

```
┌─────────────────────────────────────────────────┐
│           Web UI (Port 8080)                    │
│     Real-time Kafka Message Visualization       │
└────────────┬────────────────────────────────────┘
             │
┌────────────▼────────────────────────────────────┐
│         Kafka Broker (Port 9092)                │
│     Message Storage & Distribution              │
└─────┬──────────────────────────────────┬────────┘
      │                                   │
┌─────▼──────┐                      ┌────▼──────────┐
│ Zookeeper  │                      │   Schema      │
│  (:2181)   │                      │  Registry     │
│Coordination│                      │   (:8081)     │
└────────────┘                      └───────────────┘
      │                                   │
┌─────▼───────────────────────────────────▼────────┐
│              Producers                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │  Events  │  │   Logs   │  │ Metrics  │      │
│  └──────────┘  └──────────┘  └──────────┘      │
└──────────────────────────────────────────────────┘
             │
┌────────────▼────────────────────────────────────┐
│              Consumers                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │Analytics │  │ Alerting │  │  Logger  │      │
│  └──────────┘  └──────────┘  └──────────┘      │
└──────────────────────────────────────────────────┘
```

### Components

#### 1. Kafka Broker (Port 9092)
- Message storage and replication
- Topic management
- Partition coordination
- High-throughput message delivery

#### 2. Zookeeper (Port 2181)
- Cluster coordination
- Leader election
- Configuration management
- Distributed synchronization

#### 3. Schema Registry (Port 8081)
- Schema versioning and compatibility
- Avro schema management
- Producer/consumer schema validation
- Schema evolution support

#### 4. Event Producer
- Generates user events (clicks, purchases, signups)
- Demonstrates event-driven patterns
- Publishes to `user-events` topic
- Configurable event rates

#### 5. Log Producer
- Simulates application logs
- Multiple log levels (INFO, WARN, ERROR)
- Publishes to `application-logs` topic
- Realistic log patterns

#### 6. Metrics Producer
- System metrics (CPU, memory, disk)
- Time-series data patterns
- Publishes to `system-metrics` topic
- Demonstrates high-volume streaming

#### 7. Web UI (Port 8080)
- Real-time message visualization
- Topic browser and statistics
- Consumer group monitoring
- Message search and filtering
- Interactive Kafka management

## Quick Start

### Prerequisites

- **Docker Desktop for Mac** (running)
- **curl** (for testing scripts)
- **jq** (optional, for pretty JSON output)

### Start the Platform

```bash
# Make scripts executable
chmod +x *.sh

# Start all services
./start.sh

# Check status
./status.sh

# Stop services
./stop.sh

# Clean up everything
./cleanup.sh
```

The startup script will:
1. Check Docker is running
2. Build all containers
3. Start Zookeeper
4. Start Kafka broker
5. Create topics
6. Start producers and consumers
7. Launch web UI
8. Display access URLs

### Access the Demo

Once started, access:

- **Web UI**: http://localhost:8080
- **Kafka Broker**: localhost:9092 (internal)
- **Schema Registry**: http://localhost:8081
- **Zookeeper**: localhost:2181 (internal)

### Run Demos

```bash
# Run all demos
./demo.sh

# Test specific patterns
./demo-events.sh       # Event-driven pattern
./demo-logs.sh         # Log aggregation
./demo-metrics.sh      # Time-series data
./demo-consumer-groups.sh  # Consumer groups

# View logs
docker-compose logs -f

# Check Kafka topics
docker-compose exec kafka kafka-topics --list --bootstrap-server localhost:9092
```

## Kafka Concepts Demonstrated

### 1. Topics and Partitions

**Topics** are categories for organizing messages:
- `user-events` - User activity events (3 partitions)
- `application-logs` - Application log messages (2 partitions)
- `system-metrics` - System performance metrics (4 partitions)

**Partitions** enable:
- Parallel processing
- Scalability
- Ordered message delivery within partition
- Load balancing across consumers

```bash
# View topic details
docker-compose exec kafka kafka-topics \
  --describe \
  --topic user-events \
  --bootstrap-server localhost:9092
```

### 2. Producers

**Producers** publish messages to topics:
- Batch messages for efficiency
- Compress data (gzip, snappy, lz4)
- Handle partitioning strategies
- Provide delivery guarantees (acks)

**Demonstrated patterns:**
- Round-robin partitioning
- Key-based partitioning
- Custom partitioners
- Idempotent producers

```bash
# Monitor producer metrics
docker-compose exec kafka kafka-run-class kafka.tools.JmxTool \
  --object-name kafka.producer:type=producer-metrics,client-id=*
```

### 3. Consumers and Consumer Groups

**Consumers** read messages from topics:
- Subscribe to one or more topics
- Join consumer groups for load balancing
- Track offsets for exactly-once processing
- Handle rebalancing automatically

**Consumer Groups:**
- Each consumer group gets all messages
- Within a group, each partition assigned to one consumer
- Enables both pub/sub and queuing patterns
- Automatic failover and rebalancing

```bash
# List consumer groups
docker-compose exec kafka kafka-consumer-groups \
  --list \
  --bootstrap-server localhost:9092

# Describe consumer group
docker-compose exec kafka kafka-consumer-groups \
  --describe \
  --group analytics-group \
  --bootstrap-server localhost:9092
```

### 4. Message Delivery Guarantees

**At-most-once**: Fast but may lose messages
```python
producer.send(topic, message, acks=0)
```

**At-least-once**: No loss but duplicates possible
```python
producer.send(topic, message, acks=1)
```

**Exactly-once**: Guaranteed delivery, no duplicates
```python
producer = KafkaProducer(
    enable_idempotence=True,
    transactional_id='my-transaction-id'
)
```

### 5. Message Ordering

**Within a Partition**: Strictly ordered
- Messages with same key go to same partition
- Consumers see messages in order
- Perfect for event sourcing

**Across Partitions**: No ordering guarantee
- Parallel processing
- Higher throughput
- Use timestamp for ordering across partitions

### 6. Replication and Fault Tolerance

**Replication** (single broker demo, concept explained):
- Leader replica handles reads/writes
- Follower replicas stay in sync (ISR)
- Automatic failover on leader failure
- Configurable replication factor

**In Production:**
```bash
# Create topic with replication
kafka-topics --create \
  --topic critical-events \
  --partitions 3 \
  --replication-factor 3 \
  --bootstrap-server localhost:9092
```

### 7. Retention and Compaction

**Time-based Retention**: Delete old messages
```properties
log.retention.hours=168  # 7 days
log.retention.bytes=1073741824  # 1GB
```

**Log Compaction**: Keep latest value per key
```properties
cleanup.policy=compact
# Perfect for state/config topics
```

### 8. Stream Processing Patterns

**Event Sourcing**: Store all state changes
- Complete audit trail
- Replay events for debugging
- Temporal queries

**CQRS**: Command Query Responsibility Segregation
- Separate read and write models
- Materialized views
- Optimized queries

**Saga Pattern**: Distributed transactions
- Compensating transactions
- Event choreography
- Eventual consistency

## Web UI Features

### 1. Dashboard
- Live message throughput
- Topic statistics
- Broker health status
- Consumer lag monitoring

### 2. Topic Browser
- List all topics
- View topic configurations
- Message count per partition
- Partition leader/replica status

### 3. Message Viewer
- Real-time message stream
- Search and filter messages
- View message headers and metadata
- JSON formatting and highlighting

### 4. Consumer Groups
- Active consumer groups
- Member assignments
- Lag per partition
- Rebalancing status

### 5. Producer Testing
- Send test messages
- Choose topic and partition
- Add headers and keys
- Test different serializers

## Usage Examples

### Python Producer

```python
from kafka import KafkaProducer
import json

producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Send message
producer.send('user-events', {
    'user_id': '123',
    'event': 'purchase',
    'amount': 99.99
})

producer.flush()
```

### Python Consumer

```python
from kafka import KafkaConsumer
import json

consumer = KafkaConsumer(
    'user-events',
    bootstrap_servers=['localhost:9092'],
    group_id='analytics-group',
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

for message in consumer:
    print(f"Received: {message.value}")
```

### Command-Line Producer

```bash
docker-compose exec kafka kafka-console-producer \
  --topic user-events \
  --bootstrap-server localhost:9092
```

### Command-Line Consumer

```bash
docker-compose exec kafka kafka-console-consumer \
  --topic user-events \
  --from-beginning \
  --bootstrap-server localhost:9092
```

## Demo Scenarios

### Scenario 1: Event-Driven Architecture

Demonstrates user event processing:
```bash
./demo-events.sh
```

**Shows:**
- Event producers (click, purchase, signup)
- Multiple consumers processing same events
- Real-time analytics
- Event correlation

### Scenario 2: Log Aggregation

Demonstrates centralized logging:
```bash
./demo-logs.sh
```

**Shows:**
- Multiple services producing logs
- Centralized log collection
- Log filtering and routing
- Error alerting

### Scenario 3: Metrics Collection

Demonstrates time-series data:
```bash
./demo-metrics.sh
```

**Shows:**
- High-volume metric streaming
- Aggregation and downsampling
- Anomaly detection
- Dashboard updates

### Scenario 4: Consumer Groups

Demonstrates load balancing:
```bash
./demo-consumer-groups.sh
```

**Shows:**
- Multiple consumers in group
- Partition assignment
- Rebalancing on consumer add/remove
- Lag monitoring

## Project Structure

```
kafka/
├── docker-compose.yml          # Main orchestration
├── start.sh                    # Startup script
├── stop.sh                     # Shutdown script
├── status.sh                   # Status checker
├── cleanup.sh                  # Cleanup script
├── demo.sh                     # Main demo script
├── demo-events.sh             # Event demo
├── demo-logs.sh               # Logging demo
├── demo-metrics.sh            # Metrics demo
├── demo-consumer-groups.sh    # Consumer groups demo
├── producers/
│   ├── event-producer/
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── producer.py
│   ├── log-producer/
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── producer.py
│   └── metrics-producer/
│       ├── Dockerfile
│       ├── requirements.txt
│       └── producer.py
├── consumers/
│   ├── analytics-consumer/
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── consumer.py
│   ├── alert-consumer/
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── consumer.py
│   └── logger-consumer/
│       ├── Dockerfile
│       ├── requirements.txt
│       └── consumer.py
├── web-ui/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app.py              # Flask backend
│   ├── static/
│   │   ├── index.html
│   │   ├── styles.css
│   │   └── app.js
│   └── templates/
│       └── index.html
└── docs/
    ├── ARCHITECTURE.md     # Detailed architecture
    ├── KAFKA-CONCEPTS.md   # Kafka fundamentals
    └── QUICK-REFERENCE.md  # Command reference
```

## Technology Stack

- **Kafka**: Apache Kafka 3.6
- **Zookeeper**: 3.8
- **Schema Registry**: Confluent 7.5
- **Producers/Consumers**: Python 3.11, kafka-python
- **Web UI**: Flask, WebSocket, Bootstrap 5
- **Container**: Docker & Docker Compose

## Advanced Operations

### Topic Management

```bash
# Create topic
docker-compose exec kafka kafka-topics \
  --create \
  --topic new-topic \
  --partitions 3 \
  --replication-factor 1 \
  --bootstrap-server localhost:9092

# List topics
docker-compose exec kafka kafka-topics \
  --list \
  --bootstrap-server localhost:9092

# Describe topic
docker-compose exec kafka kafka-topics \
  --describe \
  --topic user-events \
  --bootstrap-server localhost:9092

# Delete topic
docker-compose exec kafka kafka-topics \
  --delete \
  --topic old-topic \
  --bootstrap-server localhost:9092
```

### Consumer Group Management

```bash
# List groups
docker-compose exec kafka kafka-consumer-groups \
  --list \
  --bootstrap-server localhost:9092

# Describe group
docker-compose exec kafka kafka-consumer-groups \
  --describe \
  --group analytics-group \
  --bootstrap-server localhost:9092

# Reset offsets
docker-compose exec kafka kafka-consumer-groups \
  --group analytics-group \
  --topic user-events \
  --reset-offsets \
  --to-earliest \
  --execute \
  --bootstrap-server localhost:9092
```

### Performance Testing

```bash
# Producer performance test
docker-compose exec kafka kafka-producer-perf-test \
  --topic perf-test \
  --num-records 100000 \
  --record-size 1000 \
  --throughput -1 \
  --producer-props bootstrap.servers=localhost:9092

# Consumer performance test
docker-compose exec kafka kafka-consumer-perf-test \
  --topic perf-test \
  --messages 100000 \
  --bootstrap-server localhost:9092
```

## Monitoring and Debugging

### View Messages

```bash
# From beginning
docker-compose exec kafka kafka-console-consumer \
  --topic user-events \
  --from-beginning \
  --bootstrap-server localhost:9092

# From latest
docker-compose exec kafka kafka-console-consumer \
  --topic user-events \
  --bootstrap-server localhost:9092

# With keys
docker-compose exec kafka kafka-console-consumer \
  --topic user-events \
  --from-beginning \
  --property print.key=true \
  --property key.separator=: \
  --bootstrap-server localhost:9092
```

### Check Broker Status

```bash
# Broker config
docker-compose exec kafka kafka-configs \
  --bootstrap-server localhost:9092 \
  --entity-type brokers \
  --entity-name 0 \
  --describe

# Log directories
docker-compose exec kafka ls -lh /var/lib/kafka/data
```

### Consumer Lag

```bash
# Check lag for all groups
docker-compose exec kafka kafka-consumer-groups \
  --bootstrap-server localhost:9092 \
  --all-groups \
  --describe
```

## Troubleshooting

### Kafka won't start

```bash
# Check logs
docker-compose logs kafka

# Verify Zookeeper is running
docker-compose ps zookeeper

# Check port availability
lsof -i :9092

# Clean restart
./cleanup.sh
./start.sh
```

### Consumer lag increasing

```bash
# Check consumer status
docker-compose logs analytics-consumer

# Increase consumer instances
docker-compose up -d --scale analytics-consumer=3

# Check partition distribution
docker-compose exec kafka kafka-consumer-groups \
  --describe \
  --group analytics-group \
  --bootstrap-server localhost:9092
```

### Messages not appearing

```bash
# Verify topic exists
docker-compose exec kafka kafka-topics --list --bootstrap-server localhost:9092

# Check producer logs
docker-compose logs event-producer

# Test with console producer
docker-compose exec kafka kafka-console-producer \
  --topic user-events \
  --bootstrap-server localhost:9092
```

### Web UI not loading

```bash
# Check UI status
docker-compose logs web-ui

# Verify connectivity to Kafka
docker-compose exec web-ui ping kafka

# Restart UI
docker-compose restart web-ui
```

## Best Practices

### Producer Configuration

```python
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    acks='all',  # Wait for all replicas
    retries=3,  # Retry on failure
    max_in_flight_requests_per_connection=1,  # Ordering guarantee
    compression_type='gzip',  # Reduce bandwidth
    linger_ms=10,  # Batch messages
    batch_size=16384  # Batch size in bytes
)
```

### Consumer Configuration

```python
consumer = KafkaConsumer(
    'user-events',
    bootstrap_servers=['localhost:9092'],
    group_id='analytics-group',
    auto_offset_reset='earliest',  # Start from beginning
    enable_auto_commit=False,  # Manual commit for exactly-once
    max_poll_records=500,  # Records per poll
    session_timeout_ms=30000  # Heartbeat timeout
)
```

### Topic Configuration

```bash
# Production-ready topic
kafka-topics --create \
  --topic critical-events \
  --partitions 6 \
  --replication-factor 3 \
  --config retention.ms=604800000 \
  --config compression.type=producer \
  --config min.insync.replicas=2 \
  --bootstrap-server localhost:9092
```

## Performance Tuning

### Increase Throughput

1. **Add more partitions** - parallel processing
2. **Batch messages** - reduce network overhead
3. **Compress data** - reduce bandwidth
4. **Tune buffer sizes** - optimize memory usage
5. **Use async send** - don't wait for acks

### Reduce Latency

1. **Reduce linger.ms** - send immediately
2. **Increase threads** - parallel consumption
3. **Optimize serialization** - use Avro/Protobuf
4. **Local broker** - reduce network latency
5. **Tune fetch settings** - optimal batch sizes

### Ensure Reliability

1. **Set acks=all** - wait for replicas
2. **Enable idempotence** - prevent duplicates
3. **Use transactions** - atomic operations
4. **Monitor lag** - detect consumer issues
5. **Set proper retention** - don't lose data

## Production Considerations

### High Availability

- **Multiple brokers** (3+ recommended)
- **Replication factor ≥ 3**
- **min.insync.replicas ≥ 2**
- **Rack awareness** for replica placement
- **Monitoring and alerting**

### Security

- **SSL/TLS** for encryption
- **SASL** for authentication
- **ACLs** for authorization
- **Encryption at rest**
- **Network isolation**

### Scaling

- **Horizontal scaling** - add brokers
- **Vertical scaling** - increase resources
- **Partition strategy** - plan for growth
- **Consumer groups** - parallel processing
- **Tiered storage** - archive old data

## Use Cases

This demo showcases patterns for:

1. **Event Streaming** - Real-time event processing
2. **Log Aggregation** - Centralized logging
3. **Metrics Collection** - Time-series data
4. **Stream Processing** - Data transformation
5. **Message Queue** - Async task processing
6. **Event Sourcing** - Audit trails
7. **CDC** - Change Data Capture
8. **IoT Data** - Sensor data ingestion

## Learning Resources

### Official Documentation
- [Apache Kafka Documentation](https://kafka.apache.org/documentation/)
- [Kafka Python Client](https://kafka-python.readthedocs.io/)
- [Confluent Platform](https://docs.confluent.io/)

### Books
- "Kafka: The Definitive Guide" by Neha Narkhede
- "Designing Data-Intensive Applications" by Martin Kleppmann
- "Streaming Systems" by Tyler Akidau

### Online Courses
- Confluent Kafka Fundamentals
- Udemy Kafka Courses
- LinkedIn Learning Kafka Path

## License

This is a demonstration project for educational and technical learning purposes.

## About

This project serves as a technical reference implementation demonstrating:
- Apache Kafka streaming platform
- Message broker patterns
- Producer/consumer architectures
- Stream processing concepts
- Real-time data pipelines
- Microservices communication

---

**Note**: This demo uses a single Kafka broker for simplicity. Production deployments should use multiple brokers for high availability and fault tolerance.

Ready to explore Kafka? Run `./start.sh` and open http://localhost:8080!

