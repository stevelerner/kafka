#!/bin/bash

# Kafka Streaming Platform - Startup Script
# Starts all services and verifies they're running

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}"
echo "============================================================="
echo "       Kafka Streaming Platform - Startup"
echo "============================================================="
echo -e "${NC}"

# Check if Docker is running
echo -e "${BLUE}[1/6]${NC} Checking Docker..."
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}[FAIL] Docker is not running${NC}"
    echo "Please start Docker Desktop and try again."
    exit 1
fi
echo -e "${GREEN}[OK] Docker is running${NC}"

# Check if ports are available
echo -e "${BLUE}[2/6]${NC} Checking port availability..."
PORTS=(8080 9092 2181 8081)
for port in "${PORTS[@]}"; do
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        echo -e "${RED}[FAIL] Port $port is already in use${NC}"
        echo "Please free up port $port and try again."
        exit 1
    fi
done
echo -e "${GREEN}[OK] All ports available${NC}"

# Stop any existing containers
echo -e "${BLUE}[3/6]${NC} Cleaning up old containers..."
docker-compose down --remove-orphans > /dev/null 2>&1 || true
echo -e "${GREEN}[OK] Cleanup complete${NC}"

# Build and start services
echo -e "${BLUE}[4/6]${NC} Building and starting services..."
echo "This may take a few minutes on first run..."
docker-compose build --quiet
docker-compose up -d

# Wait for services to be healthy
echo -e "${BLUE}[5/6]${NC} Waiting for services to be ready..."

# Wait for Zookeeper
echo -n "  Waiting for Zookeeper..."
for i in {1..30}; do
    if docker-compose exec -T zookeeper nc -z localhost 2181 > /dev/null 2>&1; then
        echo -e " ${GREEN}[OK]${NC}"
        break
    fi
    echo -n "."
    sleep 1
done

# Wait for Kafka
echo -n "  Waiting for Kafka broker..."
for i in {1..60}; do
    if docker-compose exec -T kafka kafka-broker-api-versions --bootstrap-server localhost:9092 > /dev/null 2>&1; then
        echo -e " ${GREEN}[OK]${NC}"
        break
    fi
    echo -n "."
    sleep 1
done

# Wait for Schema Registry
echo -n "  Waiting for Schema Registry..."
for i in {1..30}; do
    if curl -s http://localhost:8081 > /dev/null 2>&1; then
        echo -e " ${GREEN}[OK]${NC}"
        break
    fi
    echo -n "."
    sleep 1
done

# Wait for Web UI
echo -n "  Waiting for Web UI..."
for i in {1..30}; do
    if curl -s http://localhost:8080/health > /dev/null 2>&1; then
        echo -e " ${GREEN}[OK]${NC}"
        break
    fi
    echo -n "."
    sleep 1
done

# Give producers/consumers time to start
sleep 3

# Verify services
echo -e "${BLUE}[6/6]${NC} Verifying deployment..."

# List topics
echo -e "\n${CYAN}Topics created:${NC}"
docker-compose exec -T kafka kafka-topics --list --bootstrap-server localhost:9092 2>/dev/null | while read topic; do
    echo "  - $topic"
done

# Check container status
echo -e "\n${CYAN}Service status:${NC}"
docker-compose ps --format "table {{.Service}}\t{{.Status}}" | grep -v "NAME" | while read line; do
    service=$(echo $line | awk '{print $1}')
    status=$(echo $line | awk '{print $2}')
    if [[ $status == "Up" ]]; then
        echo -e "  ${GREEN}[OK]${NC} $service"
    else
        echo -e "  ${RED}[FAIL]${NC} $service"
    fi
done

# Success message
echo -e "\n${GREEN}============================================================="
echo "                Kafka Platform Ready!"
echo "=============================================================${NC}"

echo -e "\n${CYAN}Access the platform:${NC}"
echo -e "  Web UI:          ${YELLOW}http://localhost:8080${NC}"
echo -e "  Schema Registry: ${YELLOW}http://localhost:8081${NC}"
echo -e "  Kafka Broker:    ${YELLOW}localhost:9092${NC}"

echo -e "\n${CYAN}Useful commands:${NC}"
echo "  ./status.sh              - Check service status"
echo "  ./demo.sh                - Run demo scenarios"
echo "  ./stop.sh                - Stop all services"
echo "  ./cleanup.sh             - Clean up everything"

echo -e "\n${CYAN}View logs:${NC}"
echo "  docker-compose logs -f                    - All services"
echo "  docker-compose logs -f event-producer     - Event producer"
echo "  docker-compose logs -f analytics-consumer - Analytics consumer"

echo -e "\n${CYAN}Kafka CLI commands:${NC}"
echo "  docker-compose exec kafka kafka-topics --list --bootstrap-server localhost:9092"
echo "  docker-compose exec kafka kafka-console-consumer --topic user-events --from-beginning --bootstrap-server localhost:9092"

echo ""

