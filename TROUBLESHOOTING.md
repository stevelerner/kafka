# Kafka Platform - Troubleshooting Guide

## System Metrics Not Showing in Web UI

This is the most common issue. Here's how to fix it:

### Problem
You click the "System Metrics" tab but see "Loading metrics..." or "No Messages Yet" and nothing appears.

### Root Cause
The Web UI consumer may have started before metrics were produced, or the web UI container needs to be restarted to pick up messages.

### Solution

**Step 1: Verify metrics are being produced**
```bash
# Check metrics producer is running
docker-compose ps | grep metrics-producer

# Check logs (should see "Successfully connected to Kafka!" and message counts)
docker-compose logs metrics-producer --tail=20

# Consume directly from Kafka (should see JSON metrics)
docker-compose exec kafka kafka-console-consumer \
  --topic system-metrics \
  --from-beginning \
  --max-messages 3 \
  --bootstrap-server localhost:9092
```

**Step 2: Restart Web UI**
```bash
# This forces the web UI to reconnect and consume from the beginning
docker-compose restart web-ui

# Wait 10 seconds
sleep 10

# Check web UI logs
docker-compose logs web-ui --tail=20
# Should see: "Web UI consumed X messages from system-metrics"
```

**Step 3: Refresh browser**
- Go to http://localhost:8080
- Click "System Metrics" tab
- You should now see metrics like:
  ```
  CPU
  Host: web-server-01
  CPU Usage: 65.3% (8 cores)
  
  MEMORY
  Host: app-server-01
  Memory Usage: 72.1% (11520/16384 MB)
  ```

### Still Not Working?

**Check if metrics producer is actually sending:**
```bash
# This should show increasing message counts
docker-compose logs metrics-producer | grep "Sent metrics"
```

**Check if web UI is consuming:**
```bash
# Should see "Web UI consumed X messages from system-metrics"
docker-compose logs web-ui | grep system-metrics
```

**Nuclear option - full restart:**
```bash
docker-compose restart metrics-producer web-ui
sleep 15
# Refresh browser
```

---

## Other Common Issues

### Web UI Shows "No Messages Yet" for All Topics

**Cause:** Web UI started before producers

**Solution:**
```bash
docker-compose restart web-ui
# Wait 10 seconds and refresh browser
```

---

### Events or Logs Not Showing

Same solution as metrics - restart web UI:
```bash
docker-compose restart web-ui
```

The web UI now uses `auto_offset_reset='earliest'` which means it will catch up on existing messages when it starts/restarts.

---

### Kafka Won't Start

**Check ports:**
```bash
lsof -i :9092 -i :8080 -i :2181
```

**Clean restart:**
```bash
./cleanup.sh
./start.sh
```

---

### Metrics Stopped Coming

**Check producer:**
```bash
docker-compose ps | grep metrics-producer
docker-compose logs metrics-producer --tail=30
```

**Restart if crashed:**
```bash
docker-compose restart metrics-producer
```

---

## Understanding the Web UI Consumer

The Web UI runs a background consumer that:
1. Waits 3 seconds for Kafka to be ready
2. Subscribes to: user-events, application-logs, system-metrics
3. Starts consuming from the **beginning** of each topic (earliest offset)
4. Keeps the last 100 messages per topic in memory
5. Serves these via the web UI API

**Important:** If you restart the web UI, it re-consumes from the beginning and will show all recent messages.

---

## Quick Diagnostic Commands

```bash
# Check all containers
docker-compose ps

# Check all producer logs
docker-compose logs event-producer --tail=5
docker-compose logs log-producer --tail=5
docker-compose logs metrics-producer --tail=5

# Check web UI is consuming
docker-compose logs web-ui | grep "consumed"

# Manually consume from each topic
docker-compose exec kafka kafka-console-consumer \
  --topic user-events \
  --from-beginning \
  --max-messages 2 \
  --bootstrap-server localhost:9092

docker-compose exec kafka kafka-console-consumer \
  --topic application-logs \
  --from-beginning \
  --max-messages 2 \
  --bootstrap-server localhost:9092

docker-compose exec kafka kafka-console-consumer \
  --topic system-metrics \
  --from-beginning \
  --max-messages 2 \
  --bootstrap-server localhost:9092
```

---

## Getting Help

If issues persist:

1. Run `./status.sh` - shows overall status
2. Run `./test-metrics.sh` - tests metrics specifically
3. Check logs: `docker-compose logs`
4. Full restart: `./cleanup.sh` then `./start.sh`

---

## Expected Behavior

**Startup Timeline:**
- 0s: Docker containers start
- 5s: Zookeeper ready
- 15s: Kafka ready
- 20s: Topics created
- 25s: Producers connecting and sending
- 30s: Web UI consuming messages
- **30-35s: All tabs should show data**

If you access the Web UI before 30 seconds, you might need to refresh or restart the web UI container.

