#!/bin/bash

# Kafka Streaming Platform - Status Script
# Shows status of all services and Kafka topics

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}"
echo "============================================================="
echo "       Kafka Streaming Platform - Status"
echo "============================================================="
echo -e "${NC}"

# Check if services are running
echo -e "${CYAN}Container Status:${NC}"
docker-compose ps

# Check if Kafka is accessible
if docker-compose exec -T kafka kafka-broker-api-versions --bootstrap-server localhost:9092 > /dev/null 2>&1; then
    echo -e "\n${CYAN}Kafka Topics:${NC}"
    docker-compose exec -T kafka kafka-topics --list --bootstrap-server localhost:9092 2>/dev/null | while read topic; do
        echo "  • $topic"
    done
    
    echo -e "\n${CYAN}Topic Details:${NC}"
    docker-compose exec -T kafka kafka-topics --describe --bootstrap-server localhost:9092 2>/dev/null
    
    echo -e "\n${CYAN}Consumer Groups:${NC}"
    docker-compose exec -T kafka kafka-consumer-groups --list --bootstrap-server localhost:9092 2>/dev/null | while read group; do
        echo "  • $group"
    done
else
    echo -e "\n${YELLOW}WARNING: Kafka broker not accessible${NC}"
fi

# Check web UI
echo -e "\n${CYAN}Web UI:${NC}"
if curl -s http://localhost:8080/health > /dev/null 2>&1; then
    echo -e "  ${GREEN}[OK] Running at http://localhost:8080${NC}"
else
    echo -e "  ${YELLOW}[FAIL] Not accessible${NC}"
fi

echo ""

