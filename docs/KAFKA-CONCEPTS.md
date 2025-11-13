# Kafka Concepts - Comprehensive Guide

## Introduction

Apache Kafka is a distributed streaming platform designed for high-throughput, fault-tolerant, publish-subscribe messaging. This guide explains core Kafka concepts with practical examples from our demo.

## Table of Contents

1. [Core Concepts](#core-concepts)
2. [Topics and Partitions](#topics-and-partitions)
3. [Producers](#producers)
4. [Consumers](#consumers)
5. [Consumer Groups](#consumer-groups)
6. [Message Ordering](#message-ordering)
7. [Delivery Guarantees](#delivery-guarantees)
8. [Replication and Fault Tolerance](#replication-and-fault-tolerance)
9. [Performance and Tuning](#performance-and-tuning)

## Core Concepts

### Broker

A Kafka server that stores messages and serves client requests.

**Key Points**:
- Multiple brokers form a cluster
- Each broker handles reads/writes for some partitions
- Brokers manage replication and failover

**In Our Demo**:
```bash
# Connect to broker
docker-compose exec kafka bash

# Check broker config
kafka-configs --describe --entity-type brokers --entity-name 0 --bootstrap-server localhost:9092
```

### Topic

A category or feed name to which messages are published.

**Key Points**:
- Logical grouping of messages
- Can have multiple partitions
- Durable (messages retained based on policy)

**In Our Demo**:
- `user-events` - User activity
- `application-logs` - Service logs
- `system-metrics` - Performance data

```bash
# List topics
docker-compose exec kafka kafka-topics --list --bootstrap-server localhost:9092

# Create topic
docker-compose exec kafka kafka-topics \
  --create \
  --topic my-topic \
  --partitions 3 \
  --replication-factor 1 \
  --bootstrap-server localhost:9092
```

### Message

The unit of data in Kafka, consisting of a key, value, and metadata.

**Structure**:
```json
{
  "key": "user_1234",           // Optional, used for partitioning
  "value": {                     // The actual message data
    "event": "purchase",
    "amount": 99.99
  },
  "timestamp": 1234567890,      // When produced
  "headers": {},                 // Optional metadata
  "partition": 0,                // Which partition
  "offset": 12345                // Position in partition
}
```

## Topics and Partitions

### What are Partitions?

Partitions are ordered, immutable sequences of messages that are continually appended to.

**Benefits**:
1. **Scalability**: Distribute load across brokers
2. **Parallelism**: Multiple consumers can read simultaneously
3. **Ordering**: Messages within a partition are ordered
4. **Performance**: Higher throughput through parallel writes

### Partition Assignment

Messages are assigned to partitions based on:

1. **Key-based** (most common):
```python
# Same key always goes to same partition
producer.send('user-events', key='user_123', value=event)
# Partition = hash(key) % num_partitions
```

2. **Round-robin** (no key):
```python
# Distributed evenly across partitions
producer.send('user-events', value=event)
```

3. **Custom partitioner**:
```python
class CustomPartitioner:
    def partition(self, key, all_partitions, available_partitions):
        # Your logic here
        return partition_number
```

### Partition Example

```
Topic: user-events (3 partitions)

Partition 0: [msg0, msg3, msg6, msg9]
             offset: 0     1     2     3

Partition 1: [msg1, msg4, msg7]
             offset: 0     1     2

Partition 2: [msg2, msg5, msg8]
             offset: 0     1     2
```

### Demo Commands

```bash
# Describe topic partitions
docker-compose exec kafka kafka-topics \
  --describe \
  --topic user-events \
  --bootstrap-server localhost:9092

# Output shows:
# - Leader: which broker leads this partition
# - Replicas: where data is stored
# - ISR: in-sync replicas
```

## Producers

### Producer Basics

Producers publish messages to Kafka topics.

**Key Responsibilities**:
- Choose which partition to send to
- Batch messages for efficiency
- Handle failures and retries
- Compress data

### Producer Configuration

```python
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    
    # Serialization
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    key_serializer=lambda k: k.encode('utf-8'),
    
    # Reliability
    acks='all',           # Wait for all replicas (slowest, safest)
    # acks=1,            # Wait for leader only (balanced)
    # acks=0,            # Don't wait (fastest, least safe)
    
    retries=3,            # Retry failed sends
    max_in_flight_requests_per_connection=1,  # Ordering guarantee
    
    # Performance
    compression_type='gzip',  # or 'snappy', 'lz4', 'zstd'
    linger_ms=10,             # Wait up to 10ms to batch messages
    batch_size=16384,         # Batch size in bytes
    buffer_memory=33554432,   # Total memory for buffering
    
    # Idempotence (exactly-once)
    enable_idempotence=True
)
```

### Sending Messages

```python
# Fire and forget (fastest, no guarantee)
producer.send('topic', value={'data': 'value'})

# Synchronous send (blocking)
future = producer.send('topic', value={'data': 'value'})
record_metadata = future.get(timeout=10)
print(f"Partition: {record_metadata.partition}, Offset: {record_metadata.offset}")

# Asynchronous with callback
def on_send_success(record_metadata):
    print(f"Success: {record_metadata.topic}:{record_metadata.partition}:{record_metadata.offset}")

def on_send_error(excp):
    print(f"Error: {excp}")

producer.send('topic', value={'data': 'value'}).add_callback(on_send_success).add_errback(on_send_error)

# Always flush when done
producer.flush()
producer.close()
```

### Producer Patterns in Demo

**Event Producer** (High reliability):
```python
acks='all'              # Wait for all replicas
retries=3               # Retry failures
compression_type='gzip' # Compress events
```

**Metrics Producer** (High throughput):
```python
acks=1                   # Wait for leader only
compression_type='snappy' # Fast compression
batch_size=32768         # Larger batches
```

## Consumers

### Consumer Basics

Consumers read messages from Kafka topics.

**Key Responsibilities**:
- Track position (offset) in each partition
- Handle rebalancing
- Process messages
- Commit offsets

### Consumer Configuration

```python
from kafka import KafkaConsumer

consumer = KafkaConsumer(
    'topic-name',
    bootstrap_servers=['localhost:9092'],
    
    # Consumer group
    group_id='my-group',
    
    # Offset management
    auto_offset_reset='earliest',  # or 'latest', 'none'
    enable_auto_commit=True,       # Auto-commit offsets
    auto_commit_interval_ms=5000,  # Commit every 5s
    
    # Deserialization
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    key_deserializer=lambda k: k.decode('utf-8'),
    
    # Performance
    max_poll_records=100,          # Records per poll
    max_poll_interval_ms=300000,   # Max time between polls
    session_timeout_ms=30000,      # Heartbeat timeout
    fetch_min_bytes=1,             # Min data to fetch
    fetch_max_wait_ms=500          # Max wait for min bytes
)
```

### Consuming Messages

```python
# Simple consumption loop
for message in consumer:
    print(f"Topic: {message.topic}")
    print(f"Partition: {message.partition}")
    print(f"Offset: {message.offset}")
    print(f"Key: {message.key}")
    print(f"Value: {message.value}")
    print(f"Timestamp: {message.timestamp}")
```

### Manual Offset Management

```python
# Disable auto-commit for exactly-once processing
consumer = KafkaConsumer(
    'topic',
    enable_auto_commit=False,
    group_id='my-group'
)

for message in consumer:
    try:
        # Process message
        process(message.value)
        
        # Commit offset only after successful processing
        consumer.commit()
    except Exception as e:
        # Don't commit on error - message will be reprocessed
        print(f"Error processing message: {e}")
```

### Seeking to Specific Offsets

```python
# Seek to beginning
consumer.seek_to_beginning()

# Seek to end
consumer.seek_to_end()

# Seek to specific offset
from kafka import TopicPartition
tp = TopicPartition('topic', 0)
consumer.seek(tp, 100)  # Start from offset 100
```

## Consumer Groups

### What are Consumer Groups?

A consumer group is a set of consumers that work together to consume a topic.

**Key Properties**:
1. Each partition assigned to exactly one consumer in group
2. Multiple groups can consume the same topic independently
3. Automatic rebalancing when consumers join/leave
4. Shared offset tracking per group

### Consumption Models

#### 1. Pub/Sub Model (Multiple Groups)

```
Topic: user-events
  Partition 0: [msg0, msg1, msg2]
  Partition 1: [msg3, msg4, msg5]

Group A (Analytics):
  Consumer A1: reads P0
  Consumer A2: reads P1

Group B (Notifications):
  Consumer B1: reads P0
  Consumer B2: reads P1

Both groups get all messages independently!
```

#### 2. Queue Model (Single Group, Multiple Consumers)

```
Topic: tasks
  Partition 0: [task0, task3]
  Partition 1: [task1, task4]
  Partition 2: [task2, task5]

Group: workers
  Worker 1: processes P0
  Worker 2: processes P1
  Worker 3: processes P2

Each task processed by exactly one worker.
```

### Rebalancing

When consumers join or leave, partitions are reassigned.

**Triggers**:
- Consumer joins group
- Consumer leaves/crashes
- New partitions added to topic

**Example**:
```
Initial: 3 partitions, 2 consumers
  Consumer 1: P0, P1
  Consumer 2: P2

Consumer 3 joins:
  Consumer 1: P0
  Consumer 2: P1
  Consumer 3: P2

Consumer 2 fails:
  Consumer 1: P0, P1
  Consumer 3: P2
```

### Demo Commands

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

# Output shows:
# TOPIC         PARTITION  CURRENT-OFFSET  LOG-END-OFFSET  LAG  CONSUMER-ID
# user-events   0          150             160             10   consumer-1
# user-events   1          145             145             0    consumer-1
# user-events   2          148             155             7    consumer-2
```

### Scaling Consumers

```bash
# Scale up
docker-compose up -d --scale analytics-consumer=3

# Scale down
docker-compose up -d --scale analytics-consumer=1
```

**Important**: Max consumers = number of partitions

## Message Ordering

### Ordering Guarantees

**Within a Partition**: Messages are strictly ordered
- Order of writes preserved
- Consumers see messages in order
- Offset increases monotonically

**Across Partitions**: No ordering guarantee
- Partitions are independent
- Concurrent writes possible
- Use timestamps for global ordering

### Maintaining Order

**Scenario**: Process user actions in order

**Solution**: Use user ID as key
```python
# All messages for same user go to same partition
producer.send(
    'user-events',
    key=user_id,  # Same user → same partition
    value=event
)
```

**Partition Assignment**:
```
user_1234 → hash(user_1234) % 3 = 1 → Partition 1
user_5678 → hash(user_5678) % 3 = 2 → Partition 2
user_9012 → hash(user_9012) % 3 = 1 → Partition 1
```

### Out-of-Order Scenarios

**Problem**: Producer retries can cause out-of-order
```
Producer sends: msg1, msg2, msg3
msg2 fails, retries
Broker receives: msg1, msg3, msg2 (out of order!)
```

**Solution**: Limit in-flight requests
```python
producer = KafkaProducer(
    max_in_flight_requests_per_connection=1,  # Only 1 unacknowledged request
    retries=10                                 # Still retry, but in order
)
```

## Delivery Guarantees

### At-Most-Once

Messages may be lost but never delivered twice.

**Configuration**:
```python
producer = KafkaProducer(
    acks=0,      # Don't wait for acknowledgment
    retries=0    # Don't retry
)

consumer = KafkaConsumer(
    enable_auto_commit=True,
    auto_offset_reset='latest'
)
# Commit offset before processing
```

**Use Case**: Metrics, logs (some loss acceptable)

### At-Least-Once

Messages never lost but may be delivered multiple times.

**Configuration**:
```python
producer = KafkaProducer(
    acks='all',  # Wait for all replicas
    retries=3    # Retry on failure
)

consumer = KafkaConsumer(
    enable_auto_commit=False
)
# Process then commit
for msg in consumer:
    process(msg)
    consumer.commit()
```

**Use Case**: Most applications, handle duplicates in processing

### Exactly-Once

Messages delivered exactly once, no loss or duplicates.

**Configuration**:
```python
producer = KafkaProducer(
    enable_idempotence=True,     # Prevent duplicates
    transactional_id='my-txn-id' # Enable transactions
)

# Begin transaction
producer.begin_transaction()
try:
    producer.send('topic', value)
    producer.commit_transaction()
except:
    producer.abort_transaction()
```

**Use Case**: Financial transactions, exactly-once required

## Replication and Fault Tolerance

### Replication Basics

Each partition has multiple replicas across brokers.

**Example**:
```
Topic: orders, Partitions: 3, Replication Factor: 3

Broker 1: P0-Leader, P1-Follower, P2-Follower
Broker 2: P0-Follower, P1-Leader, P2-Follower  
Broker 3: P0-Follower, P1-Follower, P2-Leader
```

### Leader and Followers

**Leader**:
- Handles all reads and writes
- Maintains list of in-sync replicas (ISR)

**Followers**:
- Replicate data from leader
- Can take over if leader fails

### In-Sync Replicas (ISR)

Replicas that are caught up with the leader.

**Configuration**:
```properties
# Minimum ISR required for write
min.insync.replicas=2

# Producer acknowledgment
acks=all  # Wait for all ISR
```

**Safety**:
```python
# Prevents data loss even if leader fails
producer = KafkaProducer(
    acks='all'  # Wait for min.insync.replicas
)
```

### Failure Scenarios

**Leader Failure**:
1. Leader goes down
2. Zookeeper detects failure
3. Controller elects new leader from ISR
4. Clients automatically connect to new leader

**Broker Failure**:
1. Broker goes down
2. Partitions with leader on that broker elect new leaders
3. Replicas on other brokers take over
4. Failed broker's partitions rebalanced

## Performance and Tuning

### Producer Tuning

**Throughput**:
```python
producer = KafkaProducer(
    linger_ms=100,         # Wait longer to batch
    batch_size=32768,      # Larger batches
    compression_type='lz4', # Fast compression
    acks=1                 # Don't wait for all replicas
)
```

**Latency**:
```python
producer = KafkaProducer(
    linger_ms=0,           # Send immediately
    compression_type=None, # No compression
    acks=1                 # Leader only
)
```

**Reliability**:
```python
producer = KafkaProducer(
    acks='all',            # Wait for all replicas
    retries=10,            # Retry many times
    enable_idempotence=True # Prevent duplicates
)
```

### Consumer Tuning

**Throughput**:
```python
consumer = KafkaConsumer(
    max_poll_records=500,  # Process more per poll
    fetch_min_bytes=1024,  # Fetch at least 1KB
    fetch_max_wait_ms=100  # Wait up to 100ms
)
```

**Latency**:
```python
consumer = KafkaConsumer(
    max_poll_records=1,    # Process immediately
    fetch_min_bytes=1,     # Don't wait for batches
    fetch_max_wait_ms=0    # No waiting
)
```

### Broker Tuning

**Memory**:
```properties
# Page cache for reading
# More memory = better read performance
# Kafka uses OS page cache, not JVM heap

# Increase available memory for OS cache
```

**Disk**:
```properties
# Use fast SSDs for better write performance
log.dirs=/fast/ssd/path

# Adjust flush settings (usually OS defaults are fine)
log.flush.interval.messages=10000
log.flush.interval.ms=1000
```

**Network**:
```properties
# Increase network threads
num.network.threads=8

# Increase I/O threads
num.io.threads=16

# Adjust socket buffer sizes
socket.send.buffer.bytes=102400
socket.receive.buffer.bytes=102400
socket.request.max.bytes=104857600
```

## Best Practices

1. **Use appropriate replication factor**: 3 for production
2. **Monitor consumer lag**: Alert when lag increases
3. **Use keys for ordering**: Keep related messages in order
4. **Choose right partitioning**: Balance load across partitions
5. **Configure retention**: Based on use case and storage
6. **Enable compression**: Reduce network and storage
7. **Tune batch sizes**: Balance latency vs throughput
8. **Handle rebalancing**: Design for graceful shutdowns
9. **Monitor disk space**: Prevent broker failures
10. **Use consumer groups**: Scale processing horizontally

## Common Patterns

### Pattern 1: Event Sourcing
Store all state changes as events, replay to rebuild state.

### Pattern 2: CQRS
Separate read and write models, sync via Kafka.

### Pattern 3: CDC
Capture database changes and stream to Kafka.

### Pattern 4: Stream Processing
Transform streams in real-time (Kafka Streams, ksqlDB).

### Pattern 5: Log Aggregation
Centralize logs from multiple services.

## Resources

- [Kafka Documentation](https://kafka.apache.org/documentation/)
- [Confluent Documentation](https://docs.confluent.io/)
- [Kafka Improvement Proposals (KIPs)](https://cwiki.apache.org/confluence/display/KAFKA/Kafka+Improvement+Proposals)

