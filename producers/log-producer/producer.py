#!/usr/bin/env python3
"""
Log Producer - Generates application logs at various levels
Demonstrates centralized logging and log aggregation patterns
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
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'application-logs')
PRODUCER_INTERVAL = int(os.getenv('PRODUCER_INTERVAL', '3'))

# Initialize Faker
fake = Faker()

# Log levels and their weights (more INFO, fewer ERROR)
LOG_LEVELS = {
    'DEBUG': 0.2,
    'INFO': 0.5,
    'WARN': 0.2,
    'ERROR': 0.08,
    'FATAL': 0.02
}

# Services generating logs
SERVICES = ['api-gateway', 'user-service', 'order-service', 'payment-service', 
            'inventory-service', 'notification-service', 'auth-service']

# Log message templates
LOG_TEMPLATES = {
    'DEBUG': [
        'Processing request for endpoint {}',
        'Cache miss for key: {}',
        'Database query executed in {}ms',
        'Entering method: {}',
        'Variable state: {}',
    ],
    'INFO': [
        'Request processed successfully',
        'User {} logged in',
        'Order {} created',
        'Payment processed for amount ${}',
        'Email sent to {}',
        'Cache updated',
        'Connection established to database',
    ],
    'WARN': [
        'Slow query detected: {}ms',
        'Connection pool approaching limit',
        'Deprecated API endpoint called: {}',
        'Rate limit approaching for user {}',
        'Retry attempt {} for failed request',
        'Cache size exceeding threshold',
    ],
    'ERROR': [
        'Failed to connect to database: {}',
        'Payment gateway timeout',
        'Invalid input received: {}',
        'Authentication failed for user {}',
        'Service unavailable: {}',
        'Failed to send notification',
        'Request timeout after {}ms',
    ],
    'FATAL': [
        'Database connection lost',
        'Out of memory',
        'Critical service failure: {}',
        'Unable to recover from error',
        'System shutdown initiated',
    ]
}

def create_producer():
    """Create and return a Kafka producer"""
    return KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS.split(','),
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        key_serializer=lambda k: k.encode('utf-8') if k else None,
        acks=1,
        compression_type='gzip'
    )

def weighted_choice(choices):
    """Choose item based on weights"""
    total = sum(choices.values())
    r = random.uniform(0, total)
    upto = 0
    for choice, weight in choices.items():
        if upto + weight >= r:
            return choice
        upto += weight
    return list(choices.keys())[-1]

def generate_log():
    """Generate a realistic log entry"""
    level = weighted_choice(LOG_LEVELS)
    service = random.choice(SERVICES)
    template = random.choice(LOG_TEMPLATES[level])
    
    # Fill in template placeholders
    if '{}' in template:
        if 'user' in template.lower():
            message = template.format(f"user_{random.randint(1000, 9999)}")
        elif 'order' in template.lower():
            message = template.format(f"ORD-{random.randint(10000, 99999)}")
        elif 'ms' in template:
            message = template.format(random.randint(100, 5000))
        elif '$' in template:
            message = template.format(round(random.uniform(10, 1000), 2))
        elif '@' in template or 'email' in template.lower():
            message = template.format(fake.email())
        else:
            message = template.format(fake.word())
    else:
        message = template
    
    log_entry = {
        'timestamp': datetime.utcnow().isoformat(),
        'level': level,
        'service': service,
        'message': message,
        'host': fake.hostname(),
        'process_id': random.randint(1000, 9999),
        'thread_id': random.randint(100, 999),
    }
    
    # Add trace information for errors
    if level in ['ERROR', 'FATAL']:
        log_entry['trace_id'] = fake.uuid4()[:8]
        log_entry['stack_trace'] = f"at {fake.file_path()}.py:line {random.randint(1, 500)}"
    
    # Add request information for some logs
    if random.random() > 0.5:
        log_entry['request_id'] = fake.uuid4()[:12]
        log_entry['user_id'] = f"user_{random.randint(1000, 9999)}"
    
    return service, log_entry

def main():
    """Main producer loop"""
    print(f"Starting Log Producer...")
    print(f"Kafka Bootstrap Servers: {KAFKA_BOOTSTRAP_SERVERS}")
    print(f"Topic: {KAFKA_TOPIC}")
    print(f"Interval: {PRODUCER_INTERVAL}s")
    
    producer = create_producer()
    log_count = 0
    
    try:
        while True:
            # Generate and send log
            service, log_entry = generate_log()
            
            # Use service as key for partitioning
            future = producer.send(
                KAFKA_TOPIC,
                key=service,
                value=log_entry
            )
            
            record_metadata = future.get(timeout=10)
            
            log_count += 1
            print(f"[{log_count}] {log_entry['level']:5} | {service:20} | {log_entry['message'][:60]}")
            
            # Vary interval slightly for realism
            sleep_time = PRODUCER_INTERVAL * random.uniform(0.5, 1.5)
            time.sleep(sleep_time)
            
    except KeyboardInterrupt:
        print("\nShutting down producer...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        producer.close()
        print(f"Producer stopped. Total logs sent: {log_count}")

if __name__ == '__main__':
    main()

