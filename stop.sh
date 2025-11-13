#!/bin/bash

# Kafka Streaming Platform - Stop Script
# Stops all services gracefully

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}"
echo "============================================================="
echo "       Kafka Streaming Platform - Stopping"
echo "============================================================="
echo -e "${NC}"

echo "Stopping all services..."
docker-compose stop

echo -e "\n${GREEN}[OK] All services stopped${NC}"
echo "Containers are stopped but not removed."
echo ""
echo "To remove containers: docker-compose down"
echo "To start again: ./start.sh"
echo ""

