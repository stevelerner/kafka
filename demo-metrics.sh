#!/bin/bash

# Demo: System Metrics Collection
# Shows time-series data streaming

set -e

GREEN='\033[0;32m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m'

echo -e "${CYAN}============================================================="
echo "          Demo: System Metrics Collection"
echo "=============================================================${NC}"
echo ""
echo "This demo shows system metrics (CPU, memory, disk, network)"
echo "being collected and monitored for anomalies."
echo ""
echo -e "${MAGENTA}Producer:${NC} Multiple hosts sending metrics"
echo -e "${MAGENTA}Consumer:${NC} Logger service detecting anomalies"
echo -e "${MAGENTA}Pattern:${NC} Time-series data, monitoring"
echo ""
read -p "Press Enter to start..."

echo ""
echo -e "${GREEN}Producer logs (metrics-producer):${NC}"
docker-compose logs --tail=10 metrics-producer

echo ""
echo -e "${GREEN}Consumer logs (logger-consumer):${NC}"
docker-compose logs --tail=15 logger-consumer

echo ""
echo -e "${GREEN}Live metrics stream (30 seconds):${NC}"
timeout 30 docker-compose exec -T kafka kafka-console-consumer \
    --topic system-metrics \
    --bootstrap-server localhost:9092 2>/dev/null | while read line; do
    host=$(echo "$line" | jq -r '.host' 2>/dev/null)
    type=$(echo "$line" | jq -r '.metric_type' 2>/dev/null)
    
    case $type in
        "cpu")
            usage=$(echo "$line" | jq -r '.usage_percent' 2>/dev/null)
            echo "  [CPU] $host: ${usage}%"
            ;;
        "memory")
            usage=$(echo "$line" | jq -r '.usage_percent' 2>/dev/null)
            used=$(echo "$line" | jq -r '.used_mb' 2>/dev/null)
            total=$(echo "$line" | jq -r '.total_mb' 2>/dev/null)
            echo "  [MEM] $host: ${usage}% (${used}/${total} MB)"
            ;;
        "disk")
            usage=$(echo "$line" | jq -r '.usage_percent' 2>/dev/null)
            used=$(echo "$line" | jq -r '.used_gb' 2>/dev/null)
            total=$(echo "$line" | jq -r '.total_gb' 2>/dev/null)
            echo "  [DISK] $host: ${usage}% (${used}/${total} GB)"
            ;;
        "network")
            rx=$(echo "$line" | jq -r '.rx_bytes_per_sec' 2>/dev/null)
            tx=$(echo "$line" | jq -r '.tx_bytes_per_sec' 2>/dev/null)
            rx_mb=$(echo "scale=2; $rx / 1024 / 1024" | bc 2>/dev/null || echo "0")
            tx_mb=$(echo "scale=2; $tx / 1024 / 1024" | bc 2>/dev/null || echo "0")
            echo "  [NET] $host: RX ${rx_mb}MB/s, TX ${tx_mb}MB/s"
            ;;
    esac
done 2>/dev/null || true

echo ""
echo -e "${CYAN}Demo complete!${NC}"
echo "View real-time metrics at: http://localhost:8080"
echo ""

