#!/usr/bin/env python3
"""
Event Producer - Generates user events (clicks, purchases, signups, etc.)
Demonstrates event-driven architecture patterns
"""

import json
import os
import random
import time
from datetime import datetime
from kafka import KafkaProducer
from faker import Faker

# Configuration
KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'user-events')
PRODUCER_INTERVAL = int(os.getenv('PRODUCER_INTERVAL', '2'))

# Initialize Faker for realistic data
fake = Faker()

# Event types and their properties
EVENT_TYPES = ['click', 'purchase', 'signup', 'login', 'logout', 'view', 'search', 'cart_add', 'cart_remove']
PRODUCTS = ['Laptop', 'Phone', 'Tablet', 'Headphones', 'Mouse', 'Keyboard', 'Monitor', 'Camera', 'Speaker', 'Watch']
PAGES = ['home', 'products', 'cart', 'checkout', 'profile', 'search', 'about', 'contact']

def create_producer():
    """Create and return a Kafka producer"""
    return KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS.split(','),
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        key_serializer=lambda k: k.encode('utf-8') if k else None,
        acks='all',
        retries=3,
        compression_type='gzip',
        linger_ms=10,
        batch_size=16384
    )

def generate_event():
    """Generate a random user event"""
    event_type = random.choice(EVENT_TYPES)
    user_id = f"user_{random.randint(1000, 9999)}"
    
    event = {
        'event_id': fake.uuid4(),
        'event_type': event_type,
        'user_id': user_id,
        'timestamp': datetime.utcnow().isoformat(),
        'session_id': fake.uuid4()[:8],
        'ip_address': fake.ipv4(),
        'user_agent': fake.user_agent(),
    }
    
    # Add event-specific fields
    if event_type == 'click':
        event['element'] = random.choice(['button', 'link', 'image', 'menu'])
        event['element_id'] = f"elem_{random.randint(1, 100)}"
        
    elif event_type == 'purchase':
        event['product'] = random.choice(PRODUCTS)
        event['amount'] = round(random.uniform(9.99, 999.99), 2)
        event['quantity'] = random.randint(1, 5)
        event['currency'] = 'USD'
        
    elif event_type == 'signup':
        event['username'] = fake.user_name()
        event['email'] = fake.email()
        event['method'] = random.choice(['email', 'google', 'facebook'])
        
    elif event_type == 'login':
        event['method'] = random.choice(['password', 'oauth', 'sso'])
        event['success'] = random.choice([True, True, True, False])
        
    elif event_type == 'view':
        event['page'] = random.choice(PAGES)
        event['duration'] = random.randint(1, 300)
        
    elif event_type == 'search':
        event['query'] = fake.catch_phrase()
        event['results_count'] = random.randint(0, 100)
        
    elif event_type in ['cart_add', 'cart_remove']:
        event['product'] = random.choice(PRODUCTS)
        event['quantity'] = random.randint(1, 3)
    
    return user_id, event

def main():
    """Main producer loop"""
    print(f"Starting Event Producer...")
    print(f"Kafka Bootstrap Servers: {KAFKA_BOOTSTRAP_SERVERS}")
    print(f"Topic: {KAFKA_TOPIC}")
    print(f"Interval: {PRODUCER_INTERVAL}s")
    
    producer = create_producer()
    event_count = 0
    
    try:
        while True:
            # Generate and send event
            user_id, event = generate_event()
            
            # Use user_id as key for partitioning (same user goes to same partition)
            future = producer.send(
                KAFKA_TOPIC,
                key=user_id,
                value=event
            )
            
            # Wait for send to complete
            record_metadata = future.get(timeout=10)
            
            event_count += 1
            print(f"[{event_count}] Sent {event['event_type']} event for {user_id} "
                  f"to partition {record_metadata.partition} at offset {record_metadata.offset}")
            
            # Wait before next event
            time.sleep(PRODUCER_INTERVAL)
            
    except KeyboardInterrupt:
        print("\nShutting down producer...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        producer.close()
        print(f"Producer stopped. Total events sent: {event_count}")

if __name__ == '__main__':
    main()

