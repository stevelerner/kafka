# Kafka Platform - Scripts Reference

Quick reference for all available management and demo scripts.

## Quick Start

```bash
cd /Volumes/external/code/kafka
./start.sh                    # Start everything
open http://localhost:8080    # Open web UI
./cleanup.sh                  # Clean up when done
```

## Core Management Scripts

### `./start.sh` - Start the Platform

**What it does:**
- Checks Docker is running
- Verifies ports 8080, 9092, 2181, 8081 are available
- Cleans up any old containers
- Builds Docker images (first run: 2-3 minutes, cached after)
- Starts Zookeeper → Kafka → Schema Registry
- Creates topics: user-events, application-logs, system-metrics
- Starts producers and consumers
- Starts web UI
- Performs health checks on all services
- Displays access URLs

**When to use:**
- First time setup
- After running `./cleanup.sh`
- After system restart
- When you want a fresh start

**Output:**
- Shows startup progress for each service
- Lists created topics
- Shows service status
- Displays URLs to access platform

**Time:** 2-3 minutes first run, 30-60 seconds subsequent runs

---

### `./stop.sh` - Stop All Services

**What it does:**
- Gracefully stops all running containers
- Keeps containers, volumes, and networks intact
- Data is preserved

**When to use:**
- Pause work without losing data
- Free up system resources temporarily
- Need to restart services

**To restart after stop:**
```bash
docker-compose start    # Quick restart
# or
./start.sh             # Full restart with health checks
```

**Time:** 5-10 seconds

---

### `./cleanup.sh` - Complete Cleanup

**What it does:**
- Asks for confirmation (y/N)
- Stops all containers
- Removes all containers
- Removes all volumes (DATA IS DELETED)
- Removes all networks
- Removes custom-built images
- Keeps base Confluent images (Kafka, Zookeeper, Schema Registry)

**When to use:**
- When completely done with the demo
- Need a fresh start from scratch
- Troubleshooting persistent issues
- Free up disk space

**Warning:** All Kafka messages and data will be lost!

**Time:** 10-15 seconds

---

### `./status.sh` - Check Platform Status

**What it does:**
- Shows container status (running/stopped)
- Lists all Kafka topics
- Shows topic details (partitions, replication)
- Lists consumer groups
- Checks web UI accessibility

**When to use:**
- Verify services are running
- Check topic configuration
- View consumer group status
- Troubleshooting

**Time:** 2-3 seconds

---

## Demo Scripts

### `./demo.sh` - Interactive Demo

**What it does:**
- Step-by-step demonstration of Kafka concepts
- Demo 1: Topics and partitions
- Demo 2: Producing and consuming messages
- Demo 3: Consumer groups
- Demo 4: Application logs stream
- Demo 5: System metrics stream
- Demo 6: Message throughput statistics
- Demo 7: Web UI features
- Explains concepts and shows live data

**When to use:**
- Learning Kafka fundamentals
- Teaching Kafka to others
- Understanding the platform
- Seeing all features in action

**Interactive:** Requires pressing Enter between demos

**Time:** 10-15 minutes (full demo)

---

### `./demo-events.sh` - Event-Driven Architecture

**What it does:**
- Shows user events being generated (clicks, purchases, signups)
- Displays producer logs (event generation)
- Displays consumer logs (analytics processing)
- Shows live event stream for 30 seconds

**Demonstrates:**
- Event sourcing pattern
- Real-time event processing
- Pub/sub messaging

**Time:** 1-2 minutes

---

### `./demo-logs.sh` - Log Aggregation

**What it does:**
- Shows logs from multiple services
- Displays producer logs (log generation)
- Displays consumer logs (alert monitoring)
- Shows live log stream with color coding by level

**Demonstrates:**
- Centralized logging
- Log levels (DEBUG, INFO, WARN, ERROR, FATAL)
- Real-time alerting

**Time:** 1-2 minutes

---

### `./demo-metrics.sh` - Metrics Collection

**What it does:**
- Shows system metrics from multiple hosts
- Displays producer logs (metric generation)
- Displays consumer logs (anomaly detection)
- Shows live metrics stream (CPU, memory, disk, network)

**Demonstrates:**
- Time-series data streaming
- High-volume data ingestion
- Anomaly detection

**Time:** 1-2 minutes

---

### `./demo-consumer-groups.sh` - Consumer Groups

**What it does:**
- Lists active consumer groups
- Shows partition assignments
- Displays consumer lag
- Explains consumer group concepts

**Demonstrates:**
- Load balancing with consumer groups
- Partition-to-consumer mapping
- Consumer scaling
- Offset management

**Time:** 1-2 minutes

---

## Common Workflows

### First Time Setup

```bash
cd /Volumes/external/code/kafka
./start.sh
./status.sh
./demo.sh
open http://localhost:8080
```

### Daily Use

```bash
# Start
./start.sh

# Work with Kafka...

# Stop when done
./stop.sh

# Next day
./start.sh  # Quick restart
```

### Troubleshooting

```bash
# Check status
./status.sh

# View logs
docker-compose logs -f

# Clean restart
./cleanup.sh
./start.sh
```

### Complete Cleanup

```bash
./cleanup.sh    # Removes everything
# Confirms before proceeding
```

---

## Script Locations

All scripts are in the kafka project root:

```
/Volumes/external/code/kafka/
├── start.sh
├── stop.sh
├── cleanup.sh
├── status.sh
├── demo.sh
├── demo-events.sh
├── demo-logs.sh
├── demo-metrics.sh
└── demo-consumer-groups.sh
```

---

## Requirements

- **Docker Desktop for Mac** - Must be running
- **Ports 8080, 9092, 2181, 8081** - Must be available
- **Scripts must be executable** - Run `chmod +x *.sh` if needed

---

## Getting Help

### Script Failed?

1. Check Docker is running: `docker info`
2. Check logs: `docker-compose logs`
3. Check ports: `lsof -i :8080 -i :9092`
4. Try clean restart: `./cleanup.sh` then `./start.sh`

### Permission Denied?

```bash
chmod +x *.sh
./start.sh
```

### Port Already in Use?

```bash
lsof -i :8080    # Find what's using the port
kill -9 <PID>    # Kill the process
./start.sh       # Start again
```

---

## Advanced Usage

### Run Specific Services

```bash
docker-compose up kafka zookeeper
```

### Scale Consumers

```bash
docker-compose up -d --scale analytics-consumer=3
```

### View Specific Service Logs

```bash
docker-compose logs -f kafka
docker-compose logs -f event-producer
docker-compose logs -f analytics-consumer
```

### Execute Commands in Containers

```bash
docker-compose exec kafka kafka-topics --list --bootstrap-server localhost:9092
docker-compose exec kafka bash
```

---

## Quick Reference

| Command | Purpose |
|---------|---------|
| `./start.sh` | Start everything |
| `./stop.sh` | Stop services |
| `./cleanup.sh` | Remove everything |
| `./status.sh` | Check status |
| `./demo.sh` | Interactive demo |
| `./demo-events.sh` | Event demo |
| `./demo-logs.sh` | Logs demo |
| `./demo-metrics.sh` | Metrics demo |
| `./demo-consumer-groups.sh` | Consumer groups demo |

---

**For more information, see:**
- README.md - Full documentation
- docs/ARCHITECTURE.md - Architecture details
- docs/KAFKA-CONCEPTS.md - Kafka fundamentals
- docs/QUICK-REFERENCE.md - Command reference

