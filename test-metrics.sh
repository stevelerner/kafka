#!/bin/bash

# Quick test script to check if system metrics are being produced

echo "============================================================="
echo "Testing System Metrics"
echo "============================================================="
echo ""

# Check if metrics producer container is running
echo "1. Checking metrics producer status..."
docker-compose ps | grep metrics-producer
echo ""

# Check metrics producer logs
echo "2. Last 10 lines from metrics producer:"
echo "-------------------------------------------------------------"
docker-compose logs --tail=10 metrics-producer
echo ""

# Check if topic exists
echo "3. Checking if system-metrics topic exists..."
docker-compose exec -T kafka kafka-topics --list --bootstrap-server localhost:9092 | grep system-metrics
echo ""

# Describe topic
echo "4. Topic details:"
echo "-------------------------------------------------------------"
docker-compose exec -T kafka kafka-topics --describe --topic system-metrics --bootstrap-server localhost:9092
echo ""

# Try to consume some messages
echo "5. Attempting to consume 5 messages from system-metrics:"
echo "-------------------------------------------------------------"
docker-compose exec -T kafka kafka-console-consumer \
  --topic system-metrics \
  --from-beginning \
  --max-messages 5 \
  --timeout-ms 10000 \
  --bootstrap-server localhost:9092 2>/dev/null || echo "No messages found or timeout"

echo ""
echo "============================================================="
echo "Test complete"
echo "============================================================="

