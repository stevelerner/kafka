# Kafka Quick Reference

Quick command reference for common Kafka operations.

## Platform Management

### Start/Stop

```bash
# Start platform
./start.sh

# Stop platform  
./stop.sh

# Check status
./status.sh

# Clean up everything
./cleanup.sh
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f kafka
docker-compose logs -f event-producer
docker-compose logs -f analytics-consumer
docker-compose logs -f web-ui

# Last 50 lines
docker-compose logs --tail=50 event-producer
```

## Topic Management

### List Topics

```bash
docker-compose exec kafka kafka-topics \
  --list \
  --bootstrap-server localhost:9092
```

### Create Topic

```bash
docker-compose exec kafka kafka-topics \
  --create \
  --topic my-topic \
  --partitions 3 \
  --replication-factor 1 \
  --bootstrap-server localhost:9092
```

### Describe Topic

```bash
docker-compose exec kafka kafka-topics \
  --describe \
  --topic user-events \
  --bootstrap-server localhost:9092
```

### Delete Topic

```bash
docker-compose exec kafka kafka-topics \
  --delete \
  --topic my-topic \
  --bootstrap-server localhost:9092
```

### Alter Topic

```bash
# Increase partitions (can't decrease)
docker-compose exec kafka kafka-topics \
  --alter \
  --topic user-events \
  --partitions 5 \
  --bootstrap-server localhost:9092

# Change configuration
docker-compose exec kafka kafka-configs \
  --alter \
  --entity-type topics \
  --entity-name user-events \
  --add-config retention.ms=86400000 \
  --bootstrap-server localhost:9092
```

## Message Operations

### Produce Messages

```bash
# Console producer (interactive)
docker-compose exec kafka kafka-console-producer \
  --topic user-events \
  --bootstrap-server localhost:9092

# With keys
docker-compose exec kafka kafka-console-producer \
  --topic user-events \
  --property "parse.key=true" \
  --property "key.separator=:" \
  --bootstrap-server localhost:9092

# Then type: key:value
```

### Consume Messages

```bash
# From latest
docker-compose exec kafka kafka-console-consumer \
  --topic user-events \
  --bootstrap-server localhost:9092

# From beginning
docker-compose exec kafka kafka-console-consumer \
  --topic user-events \
  --from-beginning \
  --bootstrap-server localhost:9092

# With keys
docker-compose exec kafka kafka-console-consumer \
  --topic user-events \
  --from-beginning \
  --property print.key=true \
  --property key.separator=" => " \
  --bootstrap-server localhost:9092

# Limit messages
docker-compose exec kafka kafka-console-consumer \
  --topic user-events \
  --from-beginning \
  --max-messages 10 \
  --bootstrap-server localhost:9092
```

### Pretty Print JSON

```bash
# Consume and format with jq
docker-compose exec kafka kafka-console-consumer \
  --topic user-events \
  --from-beginning \
  --bootstrap-server localhost:9092 | jq .
```

## Consumer Group Management

### List Consumer Groups

```bash
docker-compose exec kafka kafka-consumer-groups \
  --list \
  --bootstrap-server localhost:9092
```

### Describe Consumer Group

```bash
docker-compose exec kafka kafka-consumer-groups \
  --describe \
  --group analytics-group \
  --bootstrap-server localhost:9092
```

### Check Consumer Lag

```bash
# All groups
docker-compose exec kafka kafka-consumer-groups \
  --all-groups \
  --describe \
  --bootstrap-server localhost:9092

# Specific group
docker-compose exec kafka kafka-consumer-groups \
  --group analytics-group \
  --describe \
  --bootstrap-server localhost:9092
```

### Reset Consumer Group Offsets

```bash
# Reset to beginning
docker-compose exec kafka kafka-consumer-groups \
  --group analytics-group \
  --topic user-events \
  --reset-offsets \
  --to-earliest \
  --execute \
  --bootstrap-server localhost:9092

# Reset to end
docker-compose exec kafka kafka-consumer-groups \
  --group analytics-group \
  --topic user-events \
  --reset-offsets \
  --to-latest \
  --execute \
  --bootstrap-server localhost:9092

# Reset to specific offset
docker-compose exec kafka kafka-consumer-groups \
  --group analytics-group \
  --topic user-events:0 \
  --reset-offsets \
  --to-offset 100 \
  --execute \
  --bootstrap-server localhost:9092

# Reset to datetime
docker-compose exec kafka kafka-consumer-groups \
  --group analytics-group \
  --topic user-events \
  --reset-offsets \
  --to-datetime 2024-01-01T00:00:00.000 \
  --execute \
  --bootstrap-server localhost:9092
```

### Delete Consumer Group

```bash
# Group must be empty (no active consumers)
docker-compose exec kafka kafka-consumer-groups \
  --delete \
  --group old-group \
  --bootstrap-server localhost:9092
```

## Configuration Management

### View Broker Config

```bash
docker-compose exec kafka kafka-configs \
  --describe \
  --entity-type brokers \
  --entity-name 0 \
  --bootstrap-server localhost:9092
```

### View Topic Config

```bash
docker-compose exec kafka kafka-configs \
  --describe \
  --entity-type topics \
  --entity-name user-events \
  --bootstrap-server localhost:9092
```

### Set Topic Config

```bash
# Set retention to 7 days
docker-compose exec kafka kafka-configs \
  --alter \
  --entity-type topics \
  --entity-name user-events \
  --add-config retention.ms=604800000 \
  --bootstrap-server localhost:9092

# Set max message size to 2MB
docker-compose exec kafka kafka-configs \
  --alter \
  --entity-type topics \
  --entity-name user-events \
  --add-config max.message.bytes=2097152 \
  --bootstrap-server localhost:9092

# Enable compression
docker-compose exec kafka kafka-configs \
  --alter \
  --entity-type topics \
  --entity-name user-events \
  --add-config compression.type=gzip \
  --bootstrap-server localhost:9092
```

### Remove Topic Config

```bash
docker-compose exec kafka kafka-configs \
  --alter \
  --entity-type topics \
  --entity-name user-events \
  --delete-config retention.ms \
  --bootstrap-server localhost:9092
```

## Performance Testing

### Producer Performance

```bash
docker-compose exec kafka kafka-producer-perf-test \
  --topic perf-test \
  --num-records 100000 \
  --record-size 1000 \
  --throughput -1 \
  --producer-props bootstrap.servers=localhost:9092
```

### Consumer Performance

```bash
docker-compose exec kafka kafka-consumer-perf-test \
  --topic perf-test \
  --messages 100000 \
  --bootstrap-server localhost:9092
```

## Monitoring

### Check Broker Status

```bash
# Broker API versions (health check)
docker-compose exec kafka kafka-broker-api-versions \
  --bootstrap-server localhost:9092
```

### View Log Segments

```bash
docker-compose exec kafka ls -lh /var/lib/kafka/data
```

### JMX Metrics

```bash
# Connect to JMX port (9101)
# Use JConsole, VisualVM, or Prometheus JMX Exporter
```

## Schema Registry

### List Subjects

```bash
curl http://localhost:8081/subjects
```

### Get Schema

```bash
curl http://localhost:8081/subjects/user-events-value/versions/latest
```

### Register Schema

```bash
curl -X POST http://localhost:8081/subjects/user-events-value/versions \
  -H "Content-Type: application/vnd.schemaregistry.v1+json" \
  -d '{
    "schema": "{\"type\":\"record\",\"name\":\"User\",\"fields\":[{\"name\":\"name\",\"type\":\"string\"}]}"
  }'
```

## Debugging

### Get Offset for Partition

```bash
# Latest offset
docker-compose exec kafka kafka-run-class kafka.tools.GetOffsetShell \
  --broker-list localhost:9092 \
  --topic user-events \
  --time -1

# Earliest offset
docker-compose exec kafka kafka-run-class kafka.tools.GetOffsetShell \
  --broker-list localhost:9092 \
  --topic user-events \
  --time -2
```

### Verify Consumer Group State

```bash
docker-compose exec kafka kafka-consumer-groups \
  --describe \
  --group analytics-group \
  --state \
  --bootstrap-server localhost:9092
```

### Verify Consumer Group Members

```bash
docker-compose exec kafka kafka-consumer-groups \
  --describe \
  --group analytics-group \
  --members \
  --bootstrap-server localhost:9092
```

## Python Client Examples

### Producer Example

```python
from kafka import KafkaProducer
import json

producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Send message
producer.send('user-events', {'event': 'click', 'user': '123'})
producer.flush()
producer.close()
```

### Consumer Example

```python
from kafka import KafkaConsumer
import json

consumer = KafkaConsumer(
    'user-events',
    bootstrap_servers=['localhost:9092'],
    group_id='my-group',
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

for message in consumer:
    print(message.value)
```

### Offset Management

```python
from kafka import KafkaConsumer, TopicPartition

consumer = KafkaConsumer(
    bootstrap_servers=['localhost:9092'],
    group_id='my-group',
    enable_auto_commit=False
)

# Assign partitions
tp = TopicPartition('user-events', 0)
consumer.assign([tp])

# Seek to offset
consumer.seek(tp, 100)

# Process and commit
for message in consumer:
    process(message)
    consumer.commit()
```

## Demo Scripts

```bash
# Main demo
./demo.sh

# Specific demos
./demo-events.sh          # Event-driven pattern
./demo-logs.sh            # Log aggregation
./demo-metrics.sh         # Metrics collection
./demo-consumer-groups.sh # Consumer groups
```

## Docker Commands

### Container Management

```bash
# List containers
docker-compose ps

# Restart service
docker-compose restart kafka

# Scale consumers
docker-compose up -d --scale analytics-consumer=3

# View resource usage
docker stats

# Execute command in container
docker-compose exec kafka bash
```

### Network Debugging

```bash
# Test connectivity
docker-compose exec kafka ping zookeeper

# Check ports
docker-compose exec kafka netstat -tuln

# DNS resolution
docker-compose exec kafka nslookup kafka
```

## Useful Aliases

Add to your `~/.bashrc` or `~/.zshrc`:

```bash
# Kafka aliases
alias k-topics='docker-compose exec kafka kafka-topics --bootstrap-server localhost:9092'
alias k-produce='docker-compose exec kafka kafka-console-producer --bootstrap-server localhost:9092'
alias k-consume='docker-compose exec kafka kafka-console-consumer --bootstrap-server localhost:9092'
alias k-groups='docker-compose exec kafka kafka-consumer-groups --bootstrap-server localhost:9092'
alias k-logs='docker-compose logs -f kafka'

# Usage:
# k-topics --list
# k-consume --topic user-events --from-beginning
```

## Common Issues

### Issue: Port already in use

```bash
# Find process using port
lsof -i :9092

# Kill process
kill -9 <PID>

# Or use different port in docker-compose.yml
```

### Issue: Consumer lag increasing

```bash
# Scale up consumers
docker-compose up -d --scale analytics-consumer=3

# Or increase max.poll.records
# In consumer configuration
```

### Issue: Out of disk space

```bash
# Check disk usage
df -h

# Reduce retention
docker-compose exec kafka kafka-configs \
  --alter \
  --entity-type topics \
  --entity-name user-events \
  --add-config retention.ms=3600000 \
  --bootstrap-server localhost:9092
```

### Issue: Rebalancing too often

```bash
# Increase session timeout
# In consumer configuration:
session_timeout_ms=45000
```

## Web UI

Access the web UI at: http://localhost:8080

**Features**:
- Topic overview
- Live message streams  
- Consumer group monitoring
- Message search and filtering

## Additional Resources

- **README.md** - Main documentation
- **ARCHITECTURE.md** - Detailed architecture
- **KAFKA-CONCEPTS.md** - Kafka fundamentals

## Environment Variables

```bash
# Kafka
KAFKA_BOOTSTRAP_SERVERS=localhost:9092

# Producers
PRODUCER_INTERVAL=2  # Seconds between messages

# Consumers  
KAFKA_GROUP_ID=my-group
```

## Keyboard Shortcuts (Web UI)

- `Ctrl/Cmd + R` - Refresh current view
- `Ctrl/Cmd + K` - Search messages
- `Esc` - Close modal/dialog

---

**Quick Help**: Run `./demo.sh` for an interactive demonstration of Kafka concepts.

