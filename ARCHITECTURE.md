# CodeXray System Architecture

## Overview
CodeXray follows a client-server architecture with RESTful API design.

## Components

### 1. Backend (Flask)
- **Purpose**: API server, authentication, metrics collection
- **Port**: 5000
- **Database**: SQLite (metrics.db)

### 2. Frontend (React)
- **Purpose**: User interface, data visualization
- **Technology**: React, Recharts, Tailwind CSS

### 3. Database (SQLite)
- **Tables**:
  - `metrics`: Stores CPU and memory readings
  - `alerts`: Stores threshold breach alerts


## Security Model
- SHA-256 password hashing
- Token-based authentication
- Session expiration (1 hour)
- CORS protection

## Scalability Considerations
- Background thread for metric collection
- Database indexing on timestamps
- RESTful stateless API design