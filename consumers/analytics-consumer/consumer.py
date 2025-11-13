#!/usr/bin/env python3
"""
Analytics Consumer - Processes user events for analytics
Demonstrates consumer groups and event processing patterns
"""

import json
import os
import time
from collections import Counter
from kafka import KafkaConsumer

# Configuration
KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'user-events')
KAFKA_GROUP_ID = os.getenv('KAFKA_GROUP_ID', 'analytics-group')

def create_consumer():
    """Create and return a Kafka consumer"""
    return KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS.split(','),
        group_id=KAFKA_GROUP_ID,
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        auto_commit_interval_ms=5000,
        max_poll_records=100
    )

def process_event(event):
    """Process a single event for analytics"""
    event_type = event.get('event_type', 'unknown')
    user_id = event.get('user_id', 'unknown')
    
    # Simulate analytics processing
    if event_type == 'purchase':
        amount = event.get('amount', 0)
        product = event.get('product', 'unknown')
        return f"Purchase: {user_id} bought {product} for ${amount}"
    
    elif event_type == 'signup':
        method = event.get('method', 'unknown')
        return f"Signup: New user {user_id} via {method}"
    
    elif event_type == 'login':
        success = event.get('success', False)
        status = 'SUCCESS' if success else 'FAILED'
        return f"{status} Login: {user_id} - {'successful' if success else 'failed'}"
    
    elif event_type == 'search':
        query = event.get('query', '')
        results = event.get('results_count', 0)
        return f"Search: {user_id} searched '{query}' ({results} results)"
    
    elif event_type == 'view':
        page = event.get('page', 'unknown')
        duration = event.get('duration', 0)
        return f"View: {user_id} viewed {page} for {duration}s"
    
    else:
        return f"Event: {user_id} - {event_type}"

def main():
    """Main consumer loop"""
    print(f"Starting Analytics Consumer...")
    print(f"Kafka Bootstrap Servers: {KAFKA_BOOTSTRAP_SERVERS}")
    print(f"Topic: {KAFKA_TOPIC}")
    print(f"Group ID: {KAFKA_GROUP_ID}")
    print("Waiting for messages...\n")
    
    consumer = create_consumer()
    message_count = 0
    event_type_counter = Counter()
    
    try:
        for message in consumer:
            event = message.value
            
            # Process the event
            result = process_event(event)
            
            # Track statistics
            event_type_counter[event.get('event_type', 'unknown')] += 1
            message_count += 1
            
            # Print result
            print(f"[{message_count}] Partition {message.partition}, Offset {message.offset}: {result}")
            
            # Print statistics every 50 messages
            if message_count % 50 == 0:
                print(f"\n--- Statistics (Total: {message_count}) ---")
                for event_type, count in event_type_counter.most_common():
                    print(f"  {event_type}: {count}")
                print()
            
    except KeyboardInterrupt:
        print("\nShutting down consumer...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        consumer.close()
        print(f"\nConsumer stopped. Total messages processed: {message_count}")
        if event_type_counter:
            print("\nFinal Statistics:")
            for event_type, count in event_type_counter.most_common():
                print(f"  {event_type}: {count}")

if __name__ == '__main__':
    main()

