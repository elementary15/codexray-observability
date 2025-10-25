# 🔍 CodeXray - Observability & Security Microservice Project

A comprehensive system monitoring and alerting platform that collects system metrics, generates alerts, and provides secure APIs for reporting. Built as an intern evaluation project demonstrating proficiency in data structures, security, observability, and full-stack development.

## 📋 Project Overview

This project is a full-stack application consisting of:
- **Backend**: Python Flask REST API with SQLite database
- **Frontend**: React dashboard with real-time visualization
- **Features**: User authentication, metric collection, alerting, and reporting

## 🎯 Features Implemented

### ✅ Phase 1: Fundamentals & Data Structures 
- **Log Analyzer Utility**: Parses log files and extracts statistics
  - Counts log levels (INFO, WARN, ERROR)
  - Identifies top 5 most frequent errors
  - Uses hash maps and efficient sorting algorithms

### ✅ Phase 2: Secure Coding & Encoding 
- **Password Management**: SHA-256 password hashing (no plaintext storage)
- **Session Management**: Token-based authentication with expiration
- **API Endpoints**: `/register`, `/login`, `/logout`, `/validate-session`

### ✅ Phase 3: Observability Core (30 pts)
- **Metric Collection**: Real-time CPU and Memory usage monitoring using `psutil`
- **Alert Generation**: Configurable thresholds with automatic alerting
- **Data Storage**: SQLite database for metrics and alerts with timestamps
- **Background Processing**: Continuous metric collection in separate thread

### ✅ Phase 4: Reporting API 
- **Summary Endpoint** (`/api/summary`):
  - Total alerts generated
  - Breakdown by type (CPU/Memory)
  - Last N alert timestamps
  - Average metric values for last 10 readings
- **Secure Access**: All endpoints protected by token-based authentication

### ✅ Phase 5: Web Dashboard 
- **Data Visualization**: Real-time line charts for CPU and Memory trends
- **Alert Management**: Historical alerts table with filtering
- **Configuration UI**: Dynamic threshold adjustment
- **Modern Design**: Professional, responsive interface

## 🛠️ Tech Stack

### Backend
- **Language**: Python 3.8+
- **Framework**: Flask
- **Database**: SQLite3
- **Libraries**:
  - `psutil` - System metrics collection
  - `flask-cors` - Cross-origin resource sharing
  - `hashlib` - Password hashing
  - `threading` - Background metric collection

### Frontend
- **Framework**: React
- **Visualization**: Recharts
- **Icons**: Lucide React
- **Styling**: Tailwind CSS

## 📦 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- Node.js 14+ (for frontend development)
- pip (Python package manager)

### Backend Setup

1. **Clone the repository**
```bash
git clone https://github.com/elementary15/codexray.git
cd codexray
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Create sample log file** (optional for Phase 1)
```bash
python generate_sample_logs.py
```

5. **Run the application**
```bash
python app.py
```

The server will start on `http://localhost:5000`

### Frontend Setup (Development)

If you want to run the frontend separately:

```bash
cd frontend
npm install
npm start
```

The dashboard will open on `http://localhost:3000`

## 📁 Project Structure

```
codexray/
├── app.py                      # Main Flask application
├── requirements.txt            # Python dependencies
├── generate_sample_logs.py     # Log file generator (Phase 1)
├── sample.log                  # Sample log file for testing
├── metrics.db                  # SQLite database (auto-generated)
├── README.md                   # This file
├── ARCHITECTURE.md             # System architecture documentation
├── API_DOCUMENTATION.md        # API endpoint documentation
├── tests/
│   ├── test_auth.py           # Authentication tests
│   ├── test_metrics.py        # Metrics collection tests
│   └── test_api.py            # API endpoint tests
└── frontend/
    ├── src/
    │   ├── App.js             # React dashboard component
    │   └── index.js           # Entry point
    └── package.json           # Node dependencies
```

## 🔌 API Documentation

### Base URL
```
http://localhost:5000/api
```

### Authentication Endpoints

#### Register User
```http
POST /api/register
Content-Type: application/json

{
  "username": "john_doe",
  "password": "secure_password"
}
```

**Response:**
```json
{
  "success": true,
  "message": "User registered successfully"
}
```

#### Login
```http
POST /api/login
Content-Type: application/json

{
  "username": "john_doe",
  "password": "secure_password"
}
```

**Response:**
```json
{
  "success": true,
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "username": "john_doe"
}
```

#### Validate Session
```http
GET /api/validate-session
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "message": "Session is valid"
}
```

### Metrics Endpoints

#### Get Recent Metrics
```http
GET /api/metrics?limit=20
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "timestamp": 1698765432.123,
      "cpu": 45.2,
      "memory": 62.8
    }
  ]
}
```

#### Get All Alerts
```http
GET /api/alerts
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "timestamp": 1698765432.123,
      "type": "CPU",
      "value": 85.5,
      "threshold": 80.0,
      "message": "CPU usage exceeded threshold: 85.50%"
    }
  ]
}
```

#### Get Summary Report
```http
GET /api/summary
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "totalAlerts": 15,
    "breakdown": {
      "cpu": 8,
      "memory": 7
    },
    "lastAlerts": [...],
    "averages": {
      "cpu": 67.5,
      "memory": 71.2
    }
  }
}
```

#### Update Thresholds
```http
PUT /api/thresholds
Authorization: Bearer <token>
Content-Type: application/json

{
  "cpu": 85,
  "memory": 80
}
```

### Log Analysis Endpoint

#### Analyze Logs
```http
POST /api/analyze-logs
Authorization: Bearer <token>
Content-Type: application/json

{
  "log_file": "sample.log"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "log_level_counts": {
      "INFO": 150,
      "WARN": 25,
      "ERROR": 10
    },
    "top_errors": [
      {"message": "Connection timeout", "count": 5},
      {"message": "Database error", "count": 3}
    ]
  }
}
```

## 🧪 Testing

### Run Unit Tests
```bash
python -m pytest tests/ -v
```

### Run Specific Test
```bash
python -m pytest tests/test_auth.py -v
```

### Test Coverage
```bash
python -m pytest --cov=app tests/
```

## 📊 Sample Usage

### 1. Create Sample Logs
```bash
python generate_sample_logs.py
```

### 2. Start the Server
```bash
python app.py
```

### 3. Register a User
```bash
curl -X POST http://localhost:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password123"}'
```

### 4. Login
```bash
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password123"}'
```

### 5. Get Metrics
```bash
curl -X GET http://localhost:5000/api/metrics \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### 6. Get Summary
```bash
curl -X GET http://localhost:5000/api/summary \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## 🔒 Security Features

1. **Password Hashing**: All passwords are hashed using SHA-256 before storage
2. **Session Tokens**: Cryptographically secure random tokens (256 bits)
3. **Session Expiration**: Automatic session timeout after 1 hour
4. **No Plaintext Storage**: Passwords never stored in plaintext
5. **CORS Protection**: Cross-origin resource sharing configured
6. **Authentication Required**: All sensitive endpoints require valid token

## 📈 Performance Considerations

- **Database Indexing**: Timestamps indexed for fast queries
- **Background Processing**: Metric collection runs in separate thread
- **Connection Pooling**: SQLite connections managed efficiently
- **Data Retention**: Auto-cleanup of old metrics (configurable)
- **Efficient Queries**: Optimized SQL queries with LIMIT clauses

## 🐛 Troubleshooting

### Issue: "psutil not found"
**Solution:** Install psutil
```bash
pip install psutil
```

### Issue: "Port 5000 already in use"
**Solution:** Change port in app.py or kill existing process
```bash
# Find process
lsof -i :5000

# Kill process
kill -9 <PID>
```

### Issue: "Database locked"
**Solution:** Close other connections or delete metrics.db
```bash
rm metrics.db
python app.py  # Will recreate database
```

### Issue: "CORS errors in browser"
**Solution:** Ensure flask-cors is installed
```bash
pip install flask-cors
```

## 👨‍💻 Author

**Your Name**
- GitHub: [@yourusername](https://github.com/elementary15)
- Email: vshamanth6@gmail.com

