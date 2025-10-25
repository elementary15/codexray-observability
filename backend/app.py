# app.py - Main Flask Application
from flask import Flask, request, jsonify
from flask_cors import CORS
import hashlib
import secrets
import time
import threading
import psutil
from datetime import datetime
from collections import defaultdict
import sqlite3
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# ============================================================================
# PHASE 1: LOG ANALYZER UTILITY
# ============================================================================

class LogAnalyzer:
    """
    Analyzes log files and extracts statistics about log levels and errors.
    Uses hash maps for efficient counting and sorting.
    """
    
    def __init__(self, log_file_path):
        self.log_file_path = log_file_path
        self.log_level_counts = defaultdict(int)
        self.error_messages = defaultdict(int)
    
    def parse_logs(self):
        """Parse log file and count log levels and errors."""
        try:
            with open(self.log_file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Extract log level (assuming format: [LEVEL] message)
                    if '[' in line and ']' in line:
                        start = line.index('[')
                        end = line.index(']')
                        level = line[start+1:end]
                        self.log_level_counts[level] += 1
                        
                        # Track error messages
                        if level == 'ERROR':
                            message = line[end+1:].strip()
                            self.error_messages[message] += 1
            
            return True
        except FileNotFoundError:
            print(f"Log file not found: {self.log_file_path}")
            return False
    
    def get_log_summary(self):
        """Get summary of log levels."""
        return dict(self.log_level_counts)
    
    def get_top_errors(self, n=5):
        """Get top N most frequent errors."""
        sorted_errors = sorted(
            self.error_messages.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        return sorted_errors[:n]

# ============================================================================
# PHASE 2: PASSWORD & SESSION MANAGEMENT
# ============================================================================

class SecurityManager:
    """
    Handles user authentication, password hashing, and session management.
    Implements secure password storage and session validation.
    """
    
    def __init__(self):
        self.users = {}  # {username: hashed_password}
        self.sessions = {}  # {token: {username, created_at}}
        self.session_timeout = 3600  # 1 hour in seconds
    
    def hash_password(self, password):
        """Hash password using SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register_user(self, username, password):
        """Register a new user with hashed password."""
        if username in self.users:
            return {"success": False, "error": "User already exists"}
        
        hashed_pw = self.hash_password(password)
        self.users[username] = hashed_pw
        return {"success": True, "message": "User registered successfully"}
    
    def login_user(self, username, password):
        """Authenticate user and create session."""
        if username not in self.users:
            return {"success": False, "error": "Invalid credentials"}
        
        hashed_pw = self.hash_password(password)
        if self.users[username] != hashed_pw:
            return {"success": False, "error": "Invalid credentials"}
        
        # Create session token
        token = secrets.token_urlsafe(32)
        self.sessions[token] = {
            "username": username,
            "created_at": time.time()
        }
        
        return {"success": True, "token": token, "username": username}
    
    def validate_session(self, token):
        """Validate session token and check expiration."""
        if token not in self.sessions:
            return False
        
        session = self.sessions[token]
        if time.time() - session["created_at"] > self.session_timeout:
            del self.sessions[token]
            return False
        
        return True
    
    def logout_user(self, token):
        """Remove session token."""
        if token in self.sessions:
            del self.sessions[token]
        return {"success": True, "message": "Logged out successfully"}

# ============================================================================
# PHASE 3: METRIC COLLECTION & ALERTING
# ============================================================================

class MetricsCollector:
    """
    Collects system resource metrics (CPU, Memory) and generates alerts
    when thresholds are breached. Stores data in SQLite database.
    """
    
    def __init__(self, db_path="metrics.db"):
        self.db_path = db_path
        self.thresholds = {"cpu": 80.0, "memory": 75.0}
        self.is_collecting = False
        self.collection_thread = None
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database for metrics and alerts."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL,
                cpu_usage REAL,
                memory_usage REAL
            )
        ''')
        
        # Create alerts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL,
                alert_type TEXT,
                value REAL,
                threshold REAL,
                message TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def collect_metrics(self):
        """Collect current CPU and memory usage."""
        cpu_usage = psutil.cpu_percent(interval=1)
        memory_usage = psutil.virtual_memory().percent
        timestamp = time.time()
        
        # Store metrics
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO metrics (timestamp, cpu_usage, memory_usage) VALUES (?, ?, ?)',
            (timestamp, cpu_usage, memory_usage)
        )
        conn.commit()
        conn.close()
        
        # Check thresholds and generate alerts
        self.check_thresholds(timestamp, cpu_usage, memory_usage)
        
        return {
            "timestamp": timestamp,
            "cpu": cpu_usage,
            "memory": memory_usage
        }
    
    def check_thresholds(self, timestamp, cpu_usage, memory_usage):
        """Check if metrics exceed thresholds and generate alerts."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if cpu_usage > self.thresholds["cpu"]:
            message = f"CPU usage exceeded threshold: {cpu_usage:.2f}%"
            cursor.execute(
                'INSERT INTO alerts (timestamp, alert_type, value, threshold, message) VALUES (?, ?, ?, ?, ?)',
                (timestamp, 'CPU', cpu_usage, self.thresholds["cpu"], message)
            )
        
        if memory_usage > self.thresholds["memory"]:
            message = f"Memory usage exceeded threshold: {memory_usage:.2f}%"
            cursor.execute(
                'INSERT INTO alerts (timestamp, alert_type, value, threshold, message) VALUES (?, ?, ?, ?, ?)',
                (timestamp, 'Memory', memory_usage, self.thresholds["memory"], message)
            )
        
        conn.commit()
        conn.close()
    
    def start_collection(self, interval=5):
        """Start continuous metric collection in background thread."""
        if self.is_collecting:
            return
        
        self.is_collecting = True
        
        def collect_loop():
            while self.is_collecting:
                try:
                    self.collect_metrics()
                    time.sleep(interval)
                except Exception as e:
                    print(f"Error collecting metrics: {e}")
        
        self.collection_thread = threading.Thread(target=collect_loop, daemon=True)
        self.collection_thread.start()
    
    def stop_collection(self):
        """Stop metric collection."""
        self.is_collecting = False
    
    def get_recent_metrics(self, limit=20):
        """Get recent metrics from database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            'SELECT timestamp, cpu_usage, memory_usage FROM metrics ORDER BY timestamp DESC LIMIT ?',
            (limit,)
        )
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "timestamp": row[0],
                "cpu": row[1],
                "memory": row[2]
            }
            for row in reversed(rows)
        ]
    
    def get_all_alerts(self):
        """Get all alerts from database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            'SELECT timestamp, alert_type, value, threshold, message FROM alerts ORDER BY timestamp DESC'
        )
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "timestamp": row[0],
                "type": row[1],
                "value": row[2],
                "threshold": row[3],
                "message": row[4]
            }
            for row in rows
        ]
    
    def update_thresholds(self, cpu_threshold=None, memory_threshold=None):
        """Update alert thresholds."""
        if cpu_threshold is not None:
            self.thresholds["cpu"] = float(cpu_threshold)
        if memory_threshold is not None:
            self.thresholds["memory"] = float(memory_threshold)
        
        return {"success": True, "thresholds": self.thresholds}

# ============================================================================
# PHASE 4: REST API ENDPOINTS
# ============================================================================

# Initialize managers
security_manager = SecurityManager()
metrics_collector = MetricsCollector()

# Start metric collection automatically
metrics_collector.start_collection(interval=5)

def require_auth(f):
    """Decorator to require authentication for endpoints."""
    def wrapper(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"success": False, "error": "No token provided"}), 401
        
        if token.startswith('Bearer '):
            token = token[7:]
        
        if not security_manager.validate_session(token):
            return jsonify({"success": False, "error": "Invalid or expired token"}), 401
        
        return f(*args, **kwargs)
    
    wrapper.__name__ = f.__name__
    return wrapper

# Authentication endpoints
@app.route('/api/register', methods=['POST'])
def register():
    """Register a new user."""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({"success": False, "error": "Username and password required"}), 400
    
    result = security_manager.register_user(username, password)
    return jsonify(result), 200 if result["success"] else 400

@app.route('/api/login', methods=['POST'])
def login():
    """Login user and create session."""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({"success": False, "error": "Username and password required"}), 400
    
    result = security_manager.login_user(username, password)
    return jsonify(result), 200 if result["success"] else 401

@app.route('/api/logout', methods=['POST'])
@require_auth
def logout():
    """Logout user and destroy session."""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    result = security_manager.logout_user(token)
    return jsonify(result), 200

@app.route('/api/validate-session', methods=['GET'])
@require_auth
def validate_session():
    """Validate current session."""
    return jsonify({"success": True, "message": "Session is valid"}), 200

# Metrics and alerting endpoints
@app.route('/api/metrics', methods=['GET'])
@require_auth
def get_metrics():
    """Get recent metrics."""
    limit = request.args.get('limit', 20, type=int)
    metrics = metrics_collector.get_recent_metrics(limit)
    return jsonify({"success": True, "data": metrics}), 200

@app.route('/api/alerts', methods=['GET'])
@require_auth
def get_alerts():
    """Get all alerts."""
    alerts = metrics_collector.get_all_alerts()
    return jsonify({"success": True, "data": alerts}), 200

@app.route('/api/thresholds', methods=['GET', 'PUT'])
@require_auth
def thresholds():
    """Get or update alert thresholds."""
    if request.method == 'GET':
        return jsonify({
            "success": True,
            "data": metrics_collector.thresholds
        }), 200
    
    elif request.method == 'PUT':
        data = request.get_json()
        cpu = data.get('cpu')
        memory = data.get('memory')
        result = metrics_collector.update_thresholds(cpu, memory)
        return jsonify(result), 200

@app.route('/api/summary', methods=['GET'])
@require_auth
def get_summary():
    """
    Get comprehensive summary report including:
    - Total alerts generated
    - Breakdown by type (CPU/Memory)
    - Last N alert timestamps
    - Average metric values for last 10 readings
    """
    alerts = metrics_collector.get_all_alerts()
    metrics = metrics_collector.get_recent_metrics(10)
    
    # Calculate statistics
    total_alerts = len(alerts)
    cpu_alerts = len([a for a in alerts if a["type"] == "CPU"])
    memory_alerts = len([a for a in alerts if a["type"] == "Memory"])
    
    # Calculate averages
    if metrics:
        avg_cpu = sum(m["cpu"] for m in metrics) / len(metrics)
        avg_memory = sum(m["memory"] for m in metrics) / len(metrics)
    else:
        avg_cpu = 0
        avg_memory = 0
    
    # Last 10 alerts
    last_alerts = alerts[:10]
    
    summary = {
        "totalAlerts": total_alerts,
        "breakdown": {
            "cpu": cpu_alerts,
            "memory": memory_alerts
        },
        "lastAlerts": [
            {
                "type": a["type"],
                "timestamp": datetime.fromtimestamp(a["timestamp"]).strftime('%Y-%m-%d %H:%M:%S'),
                "message": a["message"]
            }
            for a in last_alerts
        ],
        "averages": {
            "cpu": round(avg_cpu, 2),
            "memory": round(avg_memory, 2)
        }
    }
    
    return jsonify({"success": True, "data": summary}), 200

# Log analyzer endpoint
@app.route('/api/analyze-logs', methods=['POST'])
@require_auth
def analyze_logs():
    """Analyze provided log file."""
    data = request.get_json()
    log_file = data.get('log_file', 'sample.log')
    
    analyzer = LogAnalyzer(log_file)
    if not analyzer.parse_logs():
        return jsonify({
            "success": False,
            "error": "Could not parse log file"
        }), 400
    
    summary = analyzer.get_log_summary()
    top_errors = analyzer.get_top_errors(5)
    
    return jsonify({
        "success": True,
        "data": {
            "log_level_counts": summary,
            "top_errors": [
                {"message": msg, "count": count}
                for msg, count in top_errors
            ]
        }
    }), 200

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "timestamp": time.time(),
        "collecting": metrics_collector.is_collecting
    }), 200

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    print("=" * 60)
    print("CodeXray Observability & Security Microservice")
    print("=" * 60)
    print("Starting server on http://localhost:5000")
    print("API Endpoints:")
    print("  - POST /api/register")
    print("  - POST /api/login")
    print("  - POST /api/logout")
    print("  - GET  /api/validate-session")
    print("  - GET  /api/metrics")
    print("  - GET  /api/alerts")
    print("  - GET  /api/summary")
    print("  - GET/PUT /api/thresholds")
    print("  - POST /api/analyze-logs")
    print("  - GET  /api/health")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5050)