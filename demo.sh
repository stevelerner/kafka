#!/bin/bash

# Kafka Streaming Platform - Demo Script
# Demonstrates various Kafka concepts and patterns

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

echo -e "${CYAN}"
echo "============================================================="
echo "       Kafka Streaming Platform - Interactive Demo"
echo "============================================================="
echo -e "${NC}"

# Check if services are running
if ! docker-compose ps | grep -q "Up"; then
    echo -e "${YELLOW}WARNING: Services not running. Please run ./start.sh first${NC}"
    exit 1
fi

echo -e "${BLUE}This demo will showcase various Kafka concepts:${NC}"
echo "  1. Topics and Partitions"
echo "  2. Producers and Consumers"
echo "  3. Consumer Groups"
echo "  4. Message Ordering"
echo "  5. Real-time Streaming"
echo ""
read -p "Press Enter to continue..."

# Demo 1: Topics Overview
echo -e "\n${CYAN}=============================================================${NC}"
echo -e "${MAGENTA}Demo 1: Topics and Partitions${NC}"
echo -e "${CYAN}=============================================================${NC}"
echo ""
echo "Listing all topics with their partition counts:"
echo ""
docker-compose exec -T kafka kafka-topics --describe --bootstrap-server localhost:9092 2>/dev/null
echo ""
read -p "Press Enter to continue..."

# Demo 2: Produce and Consume Messages
echo -e "\n${CYAN}=============================================================${NC}"
echo -e "${MAGENTA}Demo 2: Producing and Consuming Messages${NC}"
echo -e "${CYAN}=============================================================${NC}"
echo ""
echo "Watching live messages from user-events topic (10 seconds)..."
echo ""
timeout 10 docker-compose exec -T kafka kafka-console-consumer \
    --topic user-events \
    --bootstrap-server localhost:9092 \
    --property print.key=true \
    --property key.separator=" => " \
    --max-messages 10 2>/dev/null || true
echo ""
read -p "Press Enter to continue..."

# Demo 3: Consumer Groups
echo -e "\n${CYAN}=============================================================${NC}"
echo -e "${MAGENTA}Demo 3: Consumer Groups${NC}"
echo -e "${CYAN}=============================================================${NC}"
echo ""
echo "Active consumer groups:"
echo ""
docker-compose exec -T kafka kafka-consumer-groups --list --bootstrap-server localhost:9092 2>/dev/null
echo ""
echo "Details for analytics-group:"
echo ""
docker-compose exec -T kafka kafka-consumer-groups \
    --describe \
    --group analytics-group \
    --bootstrap-server localhost:9092 2>/dev/null || echo "No data yet - group may still be initializing"
echo ""
read -p "Press Enter to continue..."

# Demo 4: Application Logs
echo -e "\n${CYAN}=============================================================${NC}"
echo -e "${MAGENTA}Demo 4: Application Logs Stream${NC}"
echo -e "${CYAN}=============================================================${NC}"
echo ""
echo "Watching application logs (10 seconds)..."
echo ""
timeout 10 docker-compose exec -T kafka kafka-console-consumer \
    --topic application-logs \
    --bootstrap-server localhost:9092 \
    --max-messages 10 2>/dev/null | jq -c '{level, service, message}' || true
echo ""
read -p "Press Enter to continue..."

# Demo 5: System Metrics
echo -e "\n${CYAN}=============================================================${NC}"
echo -e "${MAGENTA}Demo 5: System Metrics Stream${NC}"
echo -e "${CYAN}=============================================================${NC}"
echo ""
echo "Watching system metrics (10 seconds)..."
echo ""
timeout 10 docker-compose exec -T kafka kafka-console-consumer \
    --topic system-metrics \
    --bootstrap-server localhost:9092 \
    --max-messages 15 2>/dev/null | jq -c '{host, metric_type, usage_percent}' 2>/dev/null || true
echo ""
read -p "Press Enter to continue..."

# Demo 6: Message Throughput
echo -e "\n${CYAN}=============================================================${NC}"
echo -e "${MAGENTA}Demo 6: Message Throughput Statistics${NC}"
echo -e "${CYAN}=============================================================${NC}"
echo ""
echo "Counting messages in each topic..."
echo ""

for topic in user-events application-logs system-metrics; do
    # Get partition count
    partitions=$(docker-compose exec -T kafka kafka-topics --describe --topic $topic --bootstrap-server localhost:9092 2>/dev/null | grep "PartitionCount" | awk '{print $2}')
    echo -e "${GREEN}Topic: $topic${NC}"
    echo "  Partitions: $partitions"
    
    # Get consumer group lag
    docker-compose exec -T kafka kafka-consumer-groups \
        --describe \
        --group analytics-group \
        --bootstrap-server localhost:9092 2>/dev/null | grep "^$topic" || true
    echo ""
done

read -p "Press Enter to continue..."

# Demo 7: Web UI
echo -e "\n${CYAN}=============================================================${NC}"
echo -e "${MAGENTA}Demo 7: Web UI${NC}"
echo -e "${CYAN}=============================================================${NC}"
echo ""
echo "The Web UI provides real-time visualization of:"
echo "  • Topic statistics and health"
echo "  • Live message streams"
echo "  • Consumer group monitoring"
echo "  • Message search and filtering"
echo ""
echo -e "${GREEN}Access the Web UI at: ${YELLOW}http://localhost:8080${NC}"
echo ""

# Open browser (macOS)
if command -v open &> /dev/null; then
    read -p "Open Web UI in browser? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        open http://localhost:8080
    fi
fi

# Summary
echo -e "\n${CYAN}=============================================================${NC}"
echo -e "${GREEN}Demo Complete!${NC}"
echo -e "${CYAN}=============================================================${NC}"
echo ""
echo "Key Concepts Demonstrated:"
echo "  - Topics organize messages by category"
echo "  - Partitions enable parallel processing"
echo "  - Producers send messages to topics"
echo "  - Consumers read messages from topics"
echo "  - Consumer groups load balance processing"
echo "  - Messages are ordered within partitions"
echo "  - Real-time streaming handles continuous data"
echo ""
echo "Explore more:"
echo "  • View logs: docker-compose logs -f [service-name]"
echo "  • Run specific demos: ./demo-events.sh, ./demo-logs.sh, ./demo-metrics.sh"
echo "  • Check status: ./status.sh"
echo "  • Web UI: http://localhost:8080"
echo ""

