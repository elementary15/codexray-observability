**Observability & Security Microservice**

Features



**Phase 1: Log Analysis**

Parses log files and counts different log levels (INFO, WARN, ERROR)
Identifies and ranks the top 5 most frequent error messages
Uses hash maps for fast and efficient data processing

**Phase 2: Security & Authentication**

Secure user registration and login
Passwords hashed with SHA-256 (no plaintext storage)
Token-based session management with automatic expiration after 1 hour

**Phase 3: System Monitoring**

Collects real-time CPU and memory usage metrics
Generates alerts when usage exceeds configurable thresholds
Stores metrics and alerts in a SQLite database
Runs continuous background monitoring

**Phase 4: Reporting API**

Provides a REST API with secure endpoints
Returns summary reports including:
Total number of alerts generated
Breakdown of alerts by type (CPU / Memory)
Recent alert timestamps
Average metrics over the last 10 readings

**Web Dashboard**

Interactive charts showing real-time metric trends
Historical alerts in a sortable table
Allows dynamic configuration of alert thresholds
Modern, responsive user interface

**Tech Stack**

Backend: Python, Flask, SQLite, psutil
Frontend: HTML, JavaScript, Chart.js, Tailwind CSS
Security: SHA-256 hashing, token-based authentication
