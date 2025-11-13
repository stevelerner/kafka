#!/usr/bin/env python3
"""
Alert Consumer - Monitors logs and triggers alerts on errors
Demonstrates filtering and alerting patterns
"""

import json
import os
import time
from collections import defaultdict
from kafka import KafkaConsumer

# Configuration
KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'application-logs')
KAFKA_GROUP_ID = os.getenv('KAFKA_GROUP_ID', 'alert-group')

# Alert thresholds
ERROR_THRESHOLD = 5  # Trigger alert after X errors in window
WINDOW_SIZE = 60  # Time window in seconds

def create_consumer():
    """Create and return a Kafka consumer"""
    return KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS.split(','),
        group_id=KAFKA_GROUP_ID,
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        max_poll_records=100
    )

def check_alert_conditions(error_counts):
    """Check if any service exceeds error threshold"""
    alerts = []
    for service, count in error_counts.items():
        if count >= ERROR_THRESHOLD:
            alerts.append(f"ALERT: {service} has {count} errors in last {WINDOW_SIZE}s")
    return alerts

def process_log(log_entry, error_counts):
    """Process a log entry and update error tracking"""
    level = log_entry.get('level', 'INFO')
    service = log_entry.get('service', 'unknown')
    message = log_entry.get('message', '')
    
    # Track errors per service
    if level in ['ERROR', 'FATAL']:
        error_counts[service] += 1
        return f"{level}: [{service}] {message}"
    
    elif level == 'WARN':
        return f"WARN: [{service}] {message}"
    
    # Only show non-INFO logs to reduce noise
    elif level in ['DEBUG']:
        return None
    
    return None

def main():
    """Main consumer loop"""
    print(f"Starting Alert Consumer...")
    print(f"Kafka Bootstrap Servers: {KAFKA_BOOTSTRAP_SERVERS}")
    print(f"Topic: {KAFKA_TOPIC}")
    print(f"Group ID: {KAFKA_GROUP_ID}")
    print(f"Error Threshold: {ERROR_THRESHOLD} errors in {WINDOW_SIZE}s window")
    print("Monitoring for errors and warnings...\n")
    
    consumer = create_consumer()
    message_count = 0
    error_counts = defaultdict(int)
    last_reset = time.time()
    
    try:
        for message in consumer:
            log_entry = message.value
            
            # Reset error counts periodically
            if time.time() - last_reset > WINDOW_SIZE:
                # Check for alerts before reset
                alerts = check_alert_conditions(error_counts)
                if alerts:
                    print("\n" + "=" * 70)
                    for alert in alerts:
                        print(alert)
                    print("=" * 70 + "\n")
                
                error_counts.clear()
                last_reset = time.time()
            
            # Process the log
            result = process_log(log_entry, error_counts)
            message_count += 1
            
            # Print if it's an important log
            if result:
                print(f"[{message_count}] {result}")
            
            # Show summary every 100 messages
            if message_count % 100 == 0:
                total_errors = sum(error_counts.values())
                if total_errors > 0:
                    print(f"\n--- Error Summary (last {WINDOW_SIZE}s) ---")
                    for service, count in sorted(error_counts.items(), key=lambda x: x[1], reverse=True):
                        print(f"  {service}: {count} errors")
                    print()
            
    except KeyboardInterrupt:
        print("\nShutting down consumer...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        consumer.close()
        print(f"\nConsumer stopped. Total logs processed: {message_count}")

if __name__ == '__main__':
    main()

