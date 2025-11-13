#!/usr/bin/env python3
"""
Kafka Web UI - Real-time visualization of Kafka messages and topics
"""

import json
import os
import threading
import time
from collections import deque, defaultdict
from datetime import datetime
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from kafka import KafkaConsumer, KafkaAdminClient
from kafka.admin import ConfigResource, ConfigResourceType

# Configuration
KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
MAX_MESSAGES = 100  # Keep last N messages in memory

app = Flask(__name__)
CORS(app)

# Store recent messages per topic
recent_messages = defaultdict(lambda: deque(maxlen=MAX_MESSAGES))
message_counts = defaultdict(int)
stats = {
    'total_messages': 0,
    'topics': {},
    'last_update': None
}

# Lock for thread-safe access
lock = threading.Lock()

def get_kafka_admin():
    """Create Kafka admin client"""
    return KafkaAdminClient(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS.split(','),
        client_id='web-ui-admin'
    )

def get_topic_info():
    """Get information about all topics"""
    try:
        admin = get_kafka_admin()
        topics = admin.list_topics()
        
        topic_info = {}
        for topic in topics:
            metadata = admin.describe_topics([topic])
            if metadata:
                partitions = metadata[0]['partitions']
                topic_info[topic] = {
                    'name': topic,
                    'partitions': len(partitions),
                    'replication_factor': len(partitions[0]['replicas']) if partitions else 0
                }
        
        return topic_info
    except Exception as e:
        print(f"Error getting topic info: {e}")
        return {}

def consume_messages():
    """Background thread to consume messages from all topics"""
    print("Starting message consumer thread...")
    
    topics = ['user-events', 'application-logs', 'system-metrics']
    
    consumer = KafkaConsumer(
        *topics,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS.split(','),
        group_id='web-ui-consumer',
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        auto_offset_reset='latest',  # Start from latest to avoid backlog
        enable_auto_commit=True,
        consumer_timeout_ms=1000
    )
    
    print(f"Consumer started for topics: {topics}")
    
    while True:
        try:
            for message in consumer:
                with lock:
                    topic = message.topic
                    
                    # Store message with metadata
                    msg_data = {
                        'topic': topic,
                        'partition': message.partition,
                        'offset': message.offset,
                        'timestamp': datetime.fromtimestamp(message.timestamp / 1000).isoformat(),
                        'key': message.key.decode('utf-8') if message.key else None,
                        'value': message.value
                    }
                    
                    recent_messages[topic].append(msg_data)
                    message_counts[topic] += 1
                    stats['total_messages'] += 1
                    stats['last_update'] = datetime.now().isoformat()
                    
        except Exception as e:
            print(f"Consumer error: {e}")
            time.sleep(5)

# Start consumer thread
consumer_thread = threading.Thread(target=consume_messages, daemon=True)
consumer_thread.start()

@app.route('/')
def index():
    """Serve main page"""
    return render_template('index.html')

@app.route('/api/topics')
def api_topics():
    """Get list of topics with statistics"""
    topic_info = get_topic_info()
    
    with lock:
        topics_data = []
        for topic_name, info in topic_info.items():
            topics_data.append({
                'name': topic_name,
                'partitions': info['partitions'],
                'replication_factor': info['replication_factor'],
                'message_count': message_counts.get(topic_name, 0),
                'recent_messages': len(recent_messages.get(topic_name, []))
            })
    
    return jsonify({
        'topics': topics_data,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/messages/<topic>')
def api_messages(topic):
    """Get recent messages for a topic"""
    limit = request.args.get('limit', 50, type=int)
    
    with lock:
        messages = list(recent_messages.get(topic, []))
        messages = messages[-limit:]  # Get last N messages
    
    return jsonify({
        'topic': topic,
        'messages': messages,
        'count': len(messages),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/stats')
def api_stats():
    """Get overall statistics"""
    topic_info = get_topic_info()
    
    with lock:
        topic_stats = {}
        for topic in recent_messages.keys():
            topic_stats[topic] = {
                'total_consumed': message_counts[topic],
                'recent_count': len(recent_messages[topic])
            }
        
        return jsonify({
            'total_messages': stats['total_messages'],
            'total_topics': len(topic_info),
            'topics': topic_stats,
            'last_update': stats['last_update'],
            'timestamp': datetime.now().isoformat()
        })

@app.route('/api/latest/<topic>')
def api_latest(topic):
    """Get latest message from a topic"""
    with lock:
        messages = list(recent_messages.get(topic, []))
        latest = messages[-1] if messages else None
    
    return jsonify({
        'topic': topic,
        'message': latest,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print(f"Starting Kafka Web UI...")
    print(f"Kafka Bootstrap Servers: {KAFKA_BOOTSTRAP_SERVERS}")
    print(f"Access the UI at: http://localhost:8080")
    app.run(host='0.0.0.0', port=8080, debug=False, threaded=True)

