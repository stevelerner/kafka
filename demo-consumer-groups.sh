#!/bin/bash

# Demo: Consumer Groups
# Shows how consumer groups work and load balancing

set -e

GREEN='\033[0;32m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${CYAN}============================================================="
echo "              Demo: Consumer Groups"
echo "=============================================================${NC}"
echo ""
echo "This demo demonstrates how consumer groups work:"
echo "  • Each consumer group gets all messages"
echo "  • Within a group, partitions are load balanced"
echo "  • Multiple groups can process the same data differently"
echo ""
read -p "Press Enter to start..."

echo ""
echo -e "${GREEN}Active consumer groups:${NC}"
docker-compose exec -T kafka kafka-consumer-groups \
    --list \
    --bootstrap-server localhost:9092 2>/dev/null

echo ""
echo -e "${GREEN}Analytics Group Details:${NC}"
docker-compose exec -T kafka kafka-consumer-groups \
    --describe \
    --group analytics-group \
    --bootstrap-server localhost:9092 2>/dev/null || echo "Group initializing..."

echo ""
echo -e "${GREEN}Alert Group Details:${NC}"
docker-compose exec -T kafka kafka-consumer-groups \
    --describe \
    --group alert-group \
    --bootstrap-server localhost:9092 2>/dev/null || echo "Group initializing..."

echo ""
echo -e "${GREEN}Logger Group Details:${NC}"
docker-compose exec -T kafka kafka-consumer-groups \
    --describe \
    --group logger-group \
    --bootstrap-server localhost:9092 2>/dev/null || echo "Group initializing..."

echo ""
echo -e "${YELLOW}Key Observations:${NC}"
echo "  • LAG: How many messages consumer is behind"
echo "  • CURRENT-OFFSET: Latest message read by consumer"
echo "  • LOG-END-OFFSET: Latest message in partition"
echo "  • CONSUMER-ID: Which consumer is reading which partition"
echo ""

echo -e "${GREEN}Scaling demonstration:${NC}"
echo "You can scale consumers to handle more load:"
echo "  docker-compose up -d --scale analytics-consumer=3"
echo ""
echo "Kafka will automatically rebalance partitions across consumers!"
echo ""

echo -e "${CYAN}Demo complete!${NC}"
echo ""

