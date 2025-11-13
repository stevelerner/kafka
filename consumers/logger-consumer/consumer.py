#!/usr/bin/env python3
"""
Logger Consumer - Logs system metrics and detects anomalies
Demonstrates time-series processing and aggregation
"""

import json
import os
import time
from collections import defaultdict
from kafka import KafkaConsumer

# Configuration
KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'system-metrics')
KAFKA_GROUP_ID = os.getenv('KAFKA_GROUP_ID', 'logger-group')

# Anomaly detection thresholds
CPU_THRESHOLD = 85.0
MEMORY_THRESHOLD = 90.0
DISK_THRESHOLD = 95.0

def create_consumer():
    """Create and return a Kafka consumer"""
    return KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS.split(','),
        group_id=KAFKA_GROUP_ID,
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        max_poll_records=500
    )

def detect_anomaly(metric):
    """Check if metric indicates an anomaly"""
    metric_type = metric.get('metric_type')
    host = metric.get('host')
    
    if metric_type == 'cpu':
        usage = metric.get('usage_percent', 0)
        if usage > CPU_THRESHOLD:
            return f"HIGH CPU: {host} at {usage}% (threshold: {CPU_THRESHOLD}%)"
    
    elif metric_type == 'memory':
        usage = metric.get('usage_percent', 0)
        if usage > MEMORY_THRESHOLD:
            return f"HIGH MEMORY: {host} at {usage}% (threshold: {MEMORY_THRESHOLD}%)"
    
    elif metric_type == 'disk':
        usage = metric.get('usage_percent', 0)
        if usage > DISK_THRESHOLD:
            return f"HIGH DISK: {host} at {usage}% (threshold: {DISK_THRESHOLD}%)"
    
    elif metric_type == 'network':
        rx_errors = metric.get('rx_errors', 0)
        tx_errors = metric.get('tx_errors', 0)
        if rx_errors > 50 or tx_errors > 50:
            return f"NETWORK ERRORS: {host} - RX: {rx_errors}, TX: {tx_errors}"
    
    return None

def format_metric(metric):
    """Format metric for display"""
    metric_type = metric.get('metric_type')
    host = metric.get('host')
    
    if metric_type == 'cpu':
        usage = metric.get('usage_percent', 0)
        return f"CPU: {host:20} {usage:5.1f}%"
    
    elif metric_type == 'memory':
        usage = metric.get('usage_percent', 0)
        used_mb = metric.get('used_mb', 0)
        total_mb = metric.get('total_mb', 0)
        return f"MEM: {host:20} {usage:5.1f}% ({used_mb}/{total_mb} MB)"
    
    elif metric_type == 'disk':
        usage = metric.get('usage_percent', 0)
        used_gb = metric.get('used_gb', 0)
        total_gb = metric.get('total_gb', 0)
        return f"DISK: {host:20} {usage:5.1f}% ({used_gb}/{total_gb} GB)"
    
    elif metric_type == 'network':
        rx_mb = metric.get('rx_bytes_per_sec', 0) / 1024 / 1024
        tx_mb = metric.get('tx_bytes_per_sec', 0) / 1024 / 1024
        return f"NET: {host:20} RX: {rx_mb:6.2f} MB/s, TX: {tx_mb:6.2f} MB/s"
    
    return f"{metric_type}: {host}"

def main():
    """Main consumer loop"""
    print(f"Starting Logger Consumer...")
    print(f"Kafka Bootstrap Servers: {KAFKA_BOOTSTRAP_SERVERS}")
    print(f"Topic: {KAFKA_TOPIC}")
    print(f"Group ID: {KAFKA_GROUP_ID}")
    print(f"Thresholds: CPU>{CPU_THRESHOLD}%, Memory>{MEMORY_THRESHOLD}%, Disk>{DISK_THRESHOLD}%")
    print("Monitoring system metrics...\n")
    
    consumer = create_consumer()
    message_count = 0
    metric_counts = defaultdict(int)
    anomaly_count = 0
    
    try:
        for message in consumer:
            metric = message.value
            
            # Check for anomalies
            anomaly = detect_anomaly(metric)
            if anomaly:
                print(f"\n{anomaly}\n")
                anomaly_count += 1
            
            # Log metric (sample only, not all)
            if message_count % 10 == 0:  # Log every 10th metric to reduce noise
                formatted = format_metric(metric)
                print(f"[{message_count}] {formatted}")
            
            # Track statistics
            metric_type = metric.get('metric_type', 'unknown')
            metric_counts[metric_type] += 1
            message_count += 1
            
            # Print summary every 500 metrics
            if message_count % 500 == 0:
                print(f"\n--- Summary (Total: {message_count}, Anomalies: {anomaly_count}) ---")
                for mtype, count in sorted(metric_counts.items()):
                    print(f"  {mtype}: {count}")
                print()
            
    except KeyboardInterrupt:
        print("\nShutting down consumer...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        consumer.close()
        print(f"\nConsumer stopped. Total metrics processed: {message_count}")
        print(f"Anomalies detected: {anomaly_count}")
        if metric_counts:
            print("\nFinal Statistics:")
            for mtype, count in sorted(metric_counts.items()):
                print(f"  {mtype}: {count}")

if __name__ == '__main__':
    main()

