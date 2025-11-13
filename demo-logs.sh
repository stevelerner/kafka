#!/bin/bash

# Demo: Log Aggregation
# Shows centralized logging pattern

set -e

GREEN='\033[0;32m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${CYAN}============================================================="
echo "              Demo: Log Aggregation"
echo "=============================================================${NC}"
echo ""
echo "This demo shows application logs from multiple services"
echo "being aggregated and monitored for errors and warnings."
echo ""
echo -e "${MAGENTA}Producer:${NC} Multiple microservices generating logs"
echo -e "${MAGENTA}Consumer:${NC} Alert service monitoring for errors"
echo -e "${MAGENTA}Pattern:${NC} Centralized logging, alerting"
echo ""
read -p "Press Enter to start..."

echo ""
echo -e "${GREEN}Producer logs (log-producer):${NC}"
docker-compose logs --tail=10 log-producer

echo ""
echo -e "${GREEN}Consumer logs (alert-consumer):${NC}"
docker-compose logs --tail=15 alert-consumer

echo ""
echo -e "${GREEN}Live log stream with formatting (30 seconds):${NC}"
timeout 30 docker-compose exec -T kafka kafka-console-consumer \
    --topic application-logs \
    --bootstrap-server localhost:9092 2>/dev/null | while read line; do
    level=$(echo "$line" | jq -r '.level' 2>/dev/null)
    service=$(echo "$line" | jq -r '.service' 2>/dev/null)
    message=$(echo "$line" | jq -r '.message' 2>/dev/null)
    
    case $level in
        "ERROR"|"FATAL")
            echo -e "${RED}[$level]${NC} $service: $message"
            ;;
        "WARN")
            echo -e "${YELLOW}[$level]${NC} $service: $message"
            ;;
        "INFO")
            echo -e "${GREEN}[$level]${NC} $service: $message"
            ;;
        *)
            echo "[$level] $service: $message"
            ;;
    esac
done 2>/dev/null || true

echo ""
echo -e "${CYAN}Demo complete!${NC}"
echo "View real-time logs at: http://localhost:8080"
echo ""

