#!/usr/bin/env python3
"""Generate sample log file for testing Phase 1 (Log Analyzer)"""

import random
from datetime import datetime, timedelta

# Log levels and sample messages
LOG_LEVELS = {
    'INFO': [
        'Application started successfully',
        'User login successful',
        'Request processed',
        'Cache updated',
        'Task completed',
        'Service health check passed',
        'Configuration loaded',
        'Database connection established'
    ],
    'WARN': [
        'High memory usage detected',
        'Slow query performance',
        'API rate limit approaching',
        'Cache miss',
        'Deprecated function used',
        'Connection retry attempted'
    ],
    'ERROR': [
        'Database connection failed',
        'Authentication failed',
        'File not found',
        'Network timeout',
        'Invalid input received',
        'Permission denied',
        'Service unavailable',
        'Null pointer exception'
    ]
}

def generate_logs(filename='sample.log', num_entries=200):
    """Generate sample log file with random entries."""
    
    with open(filename, 'w') as f:
        current_time = datetime.now() - timedelta(hours=2)
        
        for i in range(num_entries):
            # Random log level with weighted distribution
            level = random.choices(
                ['INFO', 'WARN', 'ERROR'],
                weights=[70, 20, 10],  # 70% INFO, 20% WARN, 10% ERROR
                k=1
            )[0]
            
            # Random message from the level
            message = random.choice(LOG_LEVELS[level])
            
            # Format: timestamp [LEVEL] message
            log_entry = f"{current_time.strftime('%Y-%m-%d %H:%M:%S')} [{level}] {message}\n"
            f.write(log_entry)
            
            # Increment time randomly (1-30 seconds)
            current_time += timedelta(seconds=random.randint(1, 30))
    
    print(f"✅ Generated {num_entries} log entries in '{filename}'")
    
    # Print summary
    with open(filename, 'r') as f:
        content = f.read()
        info_count = content.count('[INFO]')
        warn_count = content.count('[WARN]')
        error_count = content.count('[ERROR]')
    
    print(f"\nLog Summary:")
    print(f"  INFO:  {info_count}")
    print(f"  WARN:  {warn_count}")
    print(f"  ERROR: {error_count}")
    print(f"  TOTAL: {info_count + warn_count + error_count}")

if __name__ == '__main__':
    generate_logs('sample.log', 200)