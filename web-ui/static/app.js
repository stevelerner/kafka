// Kafka Web UI - Frontend JavaScript

const API_BASE = '';
let refreshInterval = null;
let currentTopic = 'user-events';

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    initializeTabs();
    initializeControls();
    loadStats();
    loadTopics();
    
    // Start auto-refresh
    startAutoRefresh();
});

// Tab switching
function initializeTabs() {
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const tabId = button.dataset.tab;
            
            // Update active states
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));
            
            button.classList.add('active');
            document.getElementById(tabId).classList.add('active');
            
            // Load content for the tab
            switch(tabId) {
                case 'topics':
                    loadTopics();
                    break;
                case 'messages':
                    loadMessages(currentTopic);
                    break;
                case 'events':
                    loadStreamMessages('user-events');
                    break;
                case 'logs':
                    loadStreamMessages('application-logs');
                    break;
                case 'metrics':
                    loadStreamMessages('system-metrics');
                    break;
            }
        });
    });
}

// Controls initialization
function initializeControls() {
    const topicSelect = document.getElementById('topic-select');
    const autoRefresh = document.getElementById('auto-refresh');
    const refreshBtn = document.getElementById('refresh-btn');
    
    topicSelect.addEventListener('change', (e) => {
        currentTopic = e.target.value;
        loadMessages(currentTopic);
    });
    
    autoRefresh.addEventListener('change', (e) => {
        if (e.target.checked) {
            startAutoRefresh();
        } else {
            stopAutoRefresh();
        }
    });
    
    refreshBtn.addEventListener('click', () => {
        loadMessages(currentTopic);
        updateStatus('Refreshed');
    });
}

// Auto-refresh functionality
function startAutoRefresh() {
    stopAutoRefresh(); // Clear existing interval
    refreshInterval = setInterval(() => {
        loadStats();
        
        // Refresh active tab content
        const activeTab = document.querySelector('.tab-button.active').dataset.tab;
        switch(activeTab) {
            case 'topics':
                loadTopics();
                break;
            case 'messages':
                loadMessages(currentTopic);
                break;
            case 'events':
                loadStreamMessages('user-events');
                break;
            case 'logs':
                loadStreamMessages('application-logs');
                break;
            case 'metrics':
                loadStreamMessages('system-metrics');
                break;
        }
    }, 2000);
}

function stopAutoRefresh() {
    if (refreshInterval) {
        clearInterval(refreshInterval);
        refreshInterval = null;
    }
}

// Load overall statistics
async function loadStats() {
    try {
        const response = await fetch(`${API_BASE}/api/stats`);
        const data = await response.json();
        
        document.getElementById('total-messages').textContent = 
            data.total_messages.toLocaleString();
        document.getElementById('total-topics').textContent = 
            data.total_topics;
        
        if (data.last_update) {
            const lastUpdate = new Date(data.last_update);
            document.getElementById('last-update').textContent = 
                lastUpdate.toLocaleTimeString();
        }
        
        updateStatus('Connected');
    } catch (error) {
        console.error('Error loading stats:', error);
        updateStatus('Error', false);
    }
}

// Load topics overview
async function loadTopics() {
    const container = document.getElementById('topics-grid');
    
    try {
        const response = await fetch(`${API_BASE}/api/topics`);
        const data = await response.json();
        
        if (data.topics.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <h3>No Topics Found</h3>
                    <p>Waiting for Kafka topics to be created...</p>
                </div>
            `;
            return;
        }
        
        container.innerHTML = data.topics.map(topic => `
            <div class="topic-card">
                <div class="topic-name">${topic.name}</div>
                <div class="topic-info">
                    <div class="info-row">
                        <span class="info-label">Partitions:</span>
                        <span class="info-value">${topic.partitions}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Replication Factor:</span>
                        <span class="info-value">${topic.replication_factor}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Messages (consumed):</span>
                        <span class="info-value">${topic.message_count.toLocaleString()}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Recent Messages:</span>
                        <span class="info-value">${topic.recent_messages}</span>
                    </div>
                </div>
            </div>
        `).join('');
        
    } catch (error) {
        console.error('Error loading topics:', error);
        container.innerHTML = `
            <div class="empty-state">
                <h3>Error Loading Topics</h3>
                <p>${error.message}</p>
            </div>
        `;
    }
}

// Load messages for specific topic
async function loadMessages(topic) {
    const container = document.getElementById('messages-container');
    
    try {
        const response = await fetch(`${API_BASE}/api/messages/${topic}?limit=50`);
        const data = await response.json();
        
        if (data.messages.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <h3>No Messages Yet</h3>
                    <p>Waiting for messages in ${topic}...</p>
                </div>
            `;
            return;
        }
        
        container.innerHTML = data.messages.reverse().map(msg => {
            const timestamp = new Date(msg.timestamp).toLocaleTimeString();
            const value = JSON.stringify(msg.value, null, 2);
            
            return `
                <div class="message-card">
                    <div class="message-header">
                        <div class="message-meta">
                            <span>Partition: ${msg.partition}</span>
                            <span>Offset: ${msg.offset}</span>
                            <span>Key: ${msg.key || 'null'}</span>
                        </div>
                        <span>${timestamp}</span>
                    </div>
                    <div class="message-body">
                        <pre>${value}</pre>
                    </div>
                </div>
            `;
        }).join('');
        
    } catch (error) {
        console.error('Error loading messages:', error);
        container.innerHTML = `
            <div class="empty-state">
                <h3>Error Loading Messages</h3>
                <p>${error.message}</p>
            </div>
        `;
    }
}

// Load stream messages for specific topics (events, logs, metrics)
async function loadStreamMessages(topic) {
    let containerId;
    if (topic === 'user-events') containerId = 'events-container';
    else if (topic === 'application-logs') containerId = 'logs-container';
    else if (topic === 'system-metrics') containerId = 'metrics-container';
    else return;
    
    const container = document.getElementById(containerId);
    
    try {
        const response = await fetch(`${API_BASE}/api/messages/${topic}?limit=30`);
        const data = await response.json();
        
        if (data.messages.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <h3>No Messages Yet</h3>
                    <p>Waiting for ${topic} messages...</p>
                </div>
            `;
            return;
        }
        
        if (topic === 'user-events') {
            container.innerHTML = data.messages.reverse().map(msg => {
                const event = msg.value;
                const timestamp = new Date(msg.timestamp).toLocaleTimeString();
                const eventClass = `event-type-${event.event_type}`;
                
                return `
                    <div class="message-card ${eventClass}">
                        <div class="message-header">
                            <div class="message-meta">
                                <strong>${event.event_type.toUpperCase()}</strong>
                                <span>User: ${event.user_id}</span>
                                <span>Session: ${event.session_id}</span>
                            </div>
                            <span>${timestamp}</span>
                        </div>
                        <div class="message-body">
                            <pre>${JSON.stringify(event, null, 2)}</pre>
                        </div>
                    </div>
                `;
            }).join('');
        }
        else if (topic === 'application-logs') {
            container.innerHTML = data.messages.reverse().map(msg => {
                const log = msg.value;
                const timestamp = new Date(msg.timestamp).toLocaleTimeString();
                const levelClass = `log-level-${log.level}`;
                
                return `
                    <div class="message-card ${levelClass}">
                        <div class="message-header">
                            <div class="message-meta">
                                <strong>${log.level}</strong>
                                <span>Service: ${log.service}</span>
                                <span>Host: ${log.host}</span>
                            </div>
                            <span>${timestamp}</span>
                        </div>
                        <div class="message-body">
                            <div>${log.message}</div>
                            ${log.trace_id ? `<div style="margin-top: 5px; opacity: 0.7;">Trace ID: ${log.trace_id}</div>` : ''}
                        </div>
                    </div>
                `;
            }).join('');
        }
        else if (topic === 'system-metrics') {
            container.innerHTML = data.messages.reverse().map(msg => {
                const metric = msg.value;
                const timestamp = new Date(msg.timestamp).toLocaleTimeString();
                
                let content = '';
                if (metric.metric_type === 'cpu') {
                    content = `CPU Usage: ${metric.usage_percent}% (${metric.cores} cores)`;
                } else if (metric.metric_type === 'memory') {
                    content = `Memory Usage: ${metric.usage_percent}% (${metric.used_mb}/${metric.total_mb} MB)`;
                } else if (metric.metric_type === 'disk') {
                    content = `Disk Usage: ${metric.usage_percent}% (${metric.used_gb}/${metric.total_gb} GB) | I/O: R:${metric.read_iops} W:${metric.write_iops} IOPS`;
                } else if (metric.metric_type === 'network') {
                    const rxMb = (metric.rx_bytes_per_sec / 1024 / 1024).toFixed(2);
                    const txMb = (metric.tx_bytes_per_sec / 1024 / 1024).toFixed(2);
                    content = `Network: RX ${rxMb} MB/s, TX ${txMb} MB/s`;
                }
                
                return `
                    <div class="message-card">
                        <div class="message-header">
                            <div class="message-meta">
                                <strong>${metric.metric_type.toUpperCase()}</strong>
                                <span>Host: ${metric.host}</span>
                            </div>
                            <span>${timestamp}</span>
                        </div>
                        <div class="message-body">
                            <div>${content}</div>
                        </div>
                    </div>
                `;
            }).join('');
        }
        
    } catch (error) {
        console.error('Error loading stream messages:', error);
        container.innerHTML = `
            <div class="empty-state">
                <h3>Error Loading Messages</h3>
                <p>${error.message}</p>
            </div>
        `;
    }
}

// Update connection status
function updateStatus(text, connected = true) {
    const indicator = document.getElementById('status-indicator');
    const statusText = document.getElementById('status-text');
    
    statusText.textContent = text;
    
    if (connected) {
        indicator.style.color = 'var(--success-color)';
    } else {
        indicator.style.color = 'var(--error-color)';
    }
}

// Format bytes for display
function formatBytes(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

// Format numbers with commas
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

