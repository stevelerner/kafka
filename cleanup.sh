#!/bin/bash

# Kafka Streaming Platform - Cleanup Script
# Removes all containers, networks, volumes, and optionally images

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}"
echo "============================================================="
echo "       Kafka Streaming Platform - Cleanup"
echo "============================================================="
echo -e "${NC}"

# Ask for confirmation
echo -e "${YELLOW}WARNING: This will remove:${NC}"
echo "  • All containers"
echo "  • All volumes (data will be lost)"
echo "  • All networks"
echo ""
read -p "Continue? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cleanup cancelled."
    exit 0
fi

echo -e "\n${CYAN}Stopping and removing containers...${NC}"
docker-compose down --volumes --remove-orphans

echo -e "\n${CYAN}Removing custom images...${NC}"
# Remove only our custom-built images
docker images --format "{{.Repository}}:{{.Tag}}" | grep "^kafka-" | xargs -r docker rmi || true

echo -e "\n${GREEN}[OK] Cleanup complete${NC}"
echo ""
echo "All containers, volumes, and networks removed."
echo "Confluent images (Kafka, Zookeeper) were kept for faster restart."
echo ""
echo "To remove everything including base images:"
echo "  docker-compose down --volumes --rmi all"
echo ""
echo "To start fresh:"
echo "  ./start.sh"
echo ""

