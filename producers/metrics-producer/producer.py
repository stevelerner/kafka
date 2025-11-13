#!/usr/bin/env python3
"""
Metrics Producer - Generates system metrics (CPU, memory, disk, network)
Demonstrates time-series data and high-volume streaming patterns
"""

import json
import os
import random
import time
from datetime import datetime
from kafka import KafkaProducer

# Configuration
KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'system-metrics')
PRODUCER_INTERVAL = int(os.getenv('PRODUCER_INTERVAL', '5'))

# Simulated hosts
HOSTS = [
    'web-server-01', 'web-server-02', 'web-server-03',
    'app-server-01', 'app-server-02',
    'db-server-01', 'db-server-02',
    'cache-server-01', 'queue-server-01'
]

# Metric types
METRICS = ['cpu', 'memory', 'disk', 'network']

def create_producer():
    """Create and return a Kafka producer"""
    return KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS.split(','),
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        key_serializer=lambda k: k.encode('utf-8') if k else None,
        acks=1,
        compression_type='snappy',  # Good for metrics
        linger_ms=5,
        batch_size=32768
    )

def generate_cpu_metrics(host, base_value):
    """Generate CPU metrics"""
    return {
        'host': host,
        'metric_type': 'cpu',
        'timestamp': datetime.utcnow().isoformat(),
        'usage_percent': round(base_value + random.uniform(-10, 10), 2),
        'user_percent': round(random.uniform(10, 40), 2),
        'system_percent': round(random.uniform(5, 20), 2),
        'idle_percent': round(random.uniform(40, 85), 2),
        'cores': random.choice([4, 8, 16, 32]),
    }

def generate_memory_metrics(host, base_value):
    """Generate memory metrics"""
    total_mb = random.choice([8192, 16384, 32768, 65536])
    used_mb = int(total_mb * (base_value / 100))
    
    return {
        'host': host,
        'metric_type': 'memory',
        'timestamp': datetime.utcnow().isoformat(),
        'usage_percent': round(base_value + random.uniform(-5, 5), 2),
        'total_mb': total_mb,
        'used_mb': used_mb,
        'available_mb': total_mb - used_mb,
        'cached_mb': random.randint(1000, 5000),
        'swap_used_mb': random.randint(0, 1000),
    }

def generate_disk_metrics(host, base_value):
    """Generate disk metrics"""
    total_gb = random.choice([500, 1000, 2000, 5000])
    used_gb = int(total_gb * (base_value / 100))
    
    return {
        'host': host,
        'metric_type': 'disk',
        'timestamp': datetime.utcnow().isoformat(),
        'usage_percent': round(base_value + random.uniform(-3, 3), 2),
        'total_gb': total_gb,
        'used_gb': used_gb,
        'available_gb': total_gb - used_gb,
        'read_iops': random.randint(100, 10000),
        'write_iops': random.randint(50, 5000),
        'read_mb_per_sec': round(random.uniform(10, 500), 2),
        'write_mb_per_sec': round(random.uniform(5, 200), 2),
    }

def generate_network_metrics(host):
    """Generate network metrics"""
    return {
        'host': host,
        'metric_type': 'network',
        'timestamp': datetime.utcnow().isoformat(),
        'interface': 'eth0',
        'rx_bytes_per_sec': random.randint(1000000, 100000000),
        'tx_bytes_per_sec': random.randint(1000000, 100000000),
        'rx_packets_per_sec': random.randint(100, 10000),
        'tx_packets_per_sec': random.randint(100, 10000),
        'rx_errors': random.randint(0, 10),
        'tx_errors': random.randint(0, 10),
        'rx_dropped': random.randint(0, 5),
        'tx_dropped': random.randint(0, 5),
    }

def main():
    """Main producer loop"""
    print(f"Starting Metrics Producer...")
    print(f"Kafka Bootstrap Servers: {KAFKA_BOOTSTRAP_SERVERS}")
    print(f"Topic: {KAFKA_TOPIC}")
    print(f"Interval: {PRODUCER_INTERVAL}s")
    
    # Wait a bit for Kafka to be ready
    print("Waiting for Kafka to be ready...")
    time.sleep(5)
    
    # Retry connection
    max_retries = 10
    for attempt in range(max_retries):
        try:
            print(f"Connecting to Kafka (attempt {attempt + 1}/{max_retries})...")
            producer = create_producer()
            print("Successfully connected to Kafka!")
            break
        except Exception as e:
            print(f"Connection attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(5)
            else:
                print("Failed to connect to Kafka after max retries")
                return
    
    metric_count = 0
    
    # Track base values for each host to simulate realistic trends
    host_states = {host: {
        'cpu': random.uniform(30, 70),
        'memory': random.uniform(40, 80),
        'disk': random.uniform(50, 90)
    } for host in HOSTS}
    
    try:
        while True:
            # Generate metrics for all hosts
            for host in HOSTS:
                # Randomly drift base values for realism
                for metric_type in ['cpu', 'memory', 'disk']:
                    host_states[host][metric_type] += random.uniform(-2, 2)
                    host_states[host][metric_type] = max(10, min(95, host_states[host][metric_type]))
                
                # Generate each metric type
                metrics = [
                    generate_cpu_metrics(host, host_states[host]['cpu']),
                    generate_memory_metrics(host, host_states[host]['memory']),
                    generate_disk_metrics(host, host_states[host]['disk']),
                    generate_network_metrics(host)
                ]
                
                # Send all metrics for this host
                for metric in metrics:
                    try:
                        future = producer.send(
                            KAFKA_TOPIC,
                            key=host,
                            value=metric
                        )
                        # Wait for confirmation
                        future.get(timeout=10)
                        metric_count += 1
                    except Exception as e:
                        print(f"Error sending metric: {e}")
            
            # Flush and report
            producer.flush()
            print(f"[{metric_count}] Sent metrics for {len(HOSTS)} hosts "
                  f"({len(HOSTS) * 4} total metrics)")
            
            time.sleep(PRODUCER_INTERVAL)
            
    except KeyboardInterrupt:
        print("\nShutting down producer...")
    except Exception as e:
        print(f"Error in main loop: {e}")
        import traceback
        traceback.print_exc()
    finally:
        producer.close()
        print(f"Producer stopped. Total metrics sent: {metric_count}")

if __name__ == '__main__':
    main()

