#!/bin/bash

# Demo: Event-Driven Architecture
# Shows user events being produced and consumed

set -e

GREEN='\033[0;32m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m'

echo -e "${CYAN}============================================================="
echo "          Demo: Event-Driven Architecture"
echo "=============================================================${NC}"
echo ""
echo "This demo shows user events (clicks, purchases, signups, etc.)"
echo "being processed in real-time by the analytics consumer."
echo ""
echo -e "${MAGENTA}Producer:${NC} Generating user events"
echo -e "${MAGENTA}Consumer:${NC} Analytics service processing events"
echo -e "${MAGENTA}Pattern:${NC} Event sourcing, pub/sub"
echo ""
read -p "Press Enter to start..."

echo ""
echo -e "${GREEN}Producer logs (event-producer):${NC}"
docker-compose logs --tail=10 event-producer

echo ""
echo -e "${GREEN}Consumer logs (analytics-consumer):${NC}"
docker-compose logs --tail=10 analytics-consumer

echo ""
echo -e "${GREEN}Live event stream (30 seconds):${NC}"
timeout 30 docker-compose exec -T kafka kafka-console-consumer \
    --topic user-events \
    --bootstrap-server localhost:9092 \
    --property print.key=true \
    --property key.separator=" => " 2>/dev/null | while read line; do
    echo "$line" | jq -c '.' 2>/dev/null || echo "$line"
done

echo ""
echo -e "${CYAN}Demo complete!${NC}"
echo "View real-time visualization at: http://localhost:8080"
echo ""

